"""Manage everything about database of the SD-QKD Node."""
import asyncio
import logging
import time

from dataclasses import dataclass
from sqlite3 import OperationalError
from typing import Final
from uuid import UUID, uuid4

from fastapi import HTTPException
from orm import NoMatch

from sd_qkd_node.configs import Config
from sd_qkd_node.database import orm, shared_db
from sd_qkd_node.encoder import dump, load
from sd_qkd_node.external_api import kme_update_block
from sd_qkd_node.model import Key
from sd_qkd_node.model.errors import BlockNotFound
from sd_qkd_node.model.key_container import KeyContainer
from sd_qkd_node.utils import bit_length, collectionint_to_b64, now

# lock_keys = asyncio.Lock()
# lock_ksids = asyncio.Lock()
# lock_relay = asyncio.Lock()
lock_blocks = asyncio.Lock()
lock = asyncio.Lock()


# lock_generation_key = asyncio.Lock()


async def __clear() -> None:
    """Deletes unnecessary blocks from database.

    A block is deleted if it satisfies at least one of the following conditions:
    - It reached Config.TTL, that is: it is considered too old in order to be used for key generation.
    - Its number of available bits is 0: the block has been completely exploited for key generation.
    """
    logging.getLogger().info("INFO clearing local db from old blocks")
    await orm.Block.objects.filter(available_bits__exact=0, in_use=0).delete()
    await orm.Block.objects.filter(timestamp__lte=now() - Config.TTL, in_use=0).delete()


async def get_ksid_on_db(**kwargs) -> orm.Ksid:
    logging.getLogger().info("INFO getting ksid on db")
    if 'ksid' in kwargs.keys():
        new_args = {'ksid': kwargs['ksid']}
    elif all(k in kwargs.keys() for k in ('slave_sae_id', 'master_sae_id')):
        new_args = {'src': kwargs['master_sae_id'], 'dst': kwargs['slave_sae_id']}
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Wrong parameters"
        )
    try:
        connection: Final[orm.Ksid] = await orm.Ksid.objects.get(**new_args)
        return connection
    except NoMatch:
        raise HTTPException(
            status_code=500,
            detail=f"Ksid not found"
        )


# kwargs can be:
# key_id -> when the key is being supplied to the slave sae
# link_id -> when the key is being relayed
async def __get_key_on_db(ksid: UUID, relay: bool, **kwargs) -> orm.Key:
    logging.getLogger().info("INFO getting key on shared db")
    try:
        key: orm.Key = await orm.Key.objects.filter(ksid=ksid, relay=relay, **kwargs).first()
        return key
    except NoMatch:
        raise HTTPException(
            status_code=500,
            detail=f"Key not found for Ksid ...{str(ksid)[25:]}"
        )


async def __retrieve_key_no_relay(ksid: UUID, key_id: UUID) -> Key:
    logging.getLogger().info("INFO getting key material for no relay connection")
    orm_key: orm.Key = await __get_key_on_db(ksid=ksid, key_id=key_id, relay=False)
    if orm_key is not None:
        await __delete(key_id=orm_key.key_id)
        key_material = await __retrieve_key_material(json_instructions=orm_key.instructions)
        return Key(orm_key.key_id, key_material)
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Key not found for Ksid ...{str(ksid)[25:]}"
        )


async def __get_link_on_db_by_companion(companion: UUID) -> orm.Link:
    logging.getLogger().info("INFO getting link by companion")
    try:
        all_links: list[orm.Link] = await orm.Link.objects.all()
        for l in all_links:
            logging.getLogger().info(f"Link {l.link_id}, companion: {l.companion}")
        link = await orm.Link.objects.get(companion=companion)
        return link
    except NoMatch:
        raise HTTPException(
            status_code=500,
            detail=f"on {Config.SAE_TO_KME_PORT} Link with KME companion ...{str(companion)[25:]} not found"
        )


async def __get_encryption_key_for_relay(ksid: UUID) -> orm.Key:
    logging.getLogger().info("INFO getting encryption key for relay")
    try:
        relayed_key: Final[orm.RelayedKey] = await orm.RelayedKey.objects.get(ksid=ksid)
        key: Final[Key] = Key(key_ID=relayed_key.key_id, key=relayed_key.key)
        await relayed_key.delete()
        return key
    except NoMatch:
        raise HTTPException(
            status_code=500,
            detail=f"Encryption key for relay not found for Ksid ...{str(ksid)[25:]}"
        )


async def __get_key_first_or_last_KME(ksid: UUID, key: orm.Key, delete: bool) -> Key:
    logging.getLogger().info("INFO getting key material for first or last kme, relay connection")
    if key is not None:
        if delete:
            await __delete(key_id=key.key_id)
        key_material = await __retrieve_key_material(json_instructions=key.instructions)
        return Key(key.key_id, key_material)
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Key not found for Ksid ...{str(ksid)[25:]} (relay)"
        )


async def __retrieve_key_yes_relay(ksid: orm.Ksid, **kwargs) -> Key:
    logging.getLogger().info("INFO getting key material for relay connection")
    if not await dbms_last_kme(ksid=ksid):
        link: orm.Link
        delete_key: bool = False
        if 'kme_src' not in kwargs.keys():
            # means it wants the encryption key to forward the key
            logging.getLogger().info("retrieve_key_yes_relay NOT last kme needs encryption key")
            link = await __get_link_on_db_by_companion(companion=ksid.kme_dst)
        else:
            # means it needs the decryption key to decrypt the received one
            delete_key = True
            logging.getLogger().info("retrieve_key_yes_relay NOT last kme needs decryption key")
            link = await __get_link_on_db_by_companion(companion=kwargs['kme_src'])
        orm_key = await __get_key_on_db(ksid=ksid.ksid, relay=True, link_id=link.link_id)
        return await __get_key_first_or_last_KME(ksid=ksid.ksid, key=orm_key, delete=delete_key)
    else:
        if 'kme_src' not in kwargs.keys():
            logging.getLogger().info("retrieve_key_yes_relay last kme needs encryption key")
            return await __get_encryption_key_for_relay(ksid=ksid.ksid)
        else:
            logging.getLogger().info("retrieve_key_yes_relay last kme needs decryption key")
            link = await __get_link_on_db_by_companion(companion=kwargs['kme_src'])
            if 'key_id' in kwargs.keys():
                orm_key = await __get_key_on_db(
                    ksid=ksid.ksid, key_id=kwargs['key_id'], relay=True, link_id=link.link_id
                )
            else:
                orm_key = await __get_key_on_db(
                    ksid=ksid.ksid, relay=True, link_id=link.link_id
                )
            return await __get_key_first_or_last_KME(ksid=ksid.ksid, key=orm_key, delete=True)


# kwargs can be:
# kme_src -> when the chain of encryption keys is being created to relay a key
# key_id -> when the key is being supplied to the slave sae
# nothing -> when the decryption key to relay the key is needed
async def dbms_get_key(ksid: orm.Ksid, **kwargs) -> KeyContainer:
    logging.getLogger().info("INFO dbms_get_key")
    """Gets the key created for a Ksid."""
    await __clear()
    if not ksid.relay:
        return KeyContainer(keys=tuple([await __retrieve_key_no_relay(ksid=ksid.ksid, key_id=kwargs['key_id'])]))
    else:
        return KeyContainer(keys=tuple([await __retrieve_key_yes_relay(ksid, **kwargs)]))


async def __delete(key_id: UUID) -> None:
    """Delete the key associated to the given key_id."""
    logging.getLogger().info("INFO deleting key from db")
    try:
        await orm.Key.objects.filter(key_id=key_id).delete()
    except NoMatch:
        raise HTTPException(
            status_code=500,
            detail="Key to delete not found"
        )


async def __create_key_on_db(key_id: UUID, ksid: UUID, instructions: object, **kwargs) -> None:
    logging.getLogger().info("INFO creating key on db")
    await orm.Key.objects.create(key_id=key_id, ksid=ksid, instructions=instructions, **kwargs)


async def __common_key_generation(connection: orm.Ksid, size: int, **kwargs) -> Key:
    logging.getLogger().info("INFO common key generation")
    link: orm.Link = await __get_link_on_db_by_companion(companion=connection.kme_dst)
    transaction = await shared_db.transaction()
    async with lock:
        try:
            key_id: UUID = uuid4()
            key_material, json_instructions = await __generate_key_material(req_bitlength=size, link_id=link.link_id)
            await __create_key_on_db(key_id=key_id, ksid=connection.ksid, instructions=json_instructions, **kwargs)
            logging.getLogger().info(f"INFO generated key {key_material} for ksid {connection.ksid}")
        except:
            await transaction.rollback()
        else:
            await transaction.commit()
            return Key(key_id, key_material)


async def dbms_generate_key(
        ksid: orm.Ksid, size: int, relay: bool
) -> Key | tuple[Key | None, UUID] | None:
    """Generates one new random key both in normal and relay mode."""
    logging.getLogger().info("INFO start generate key")
    if not relay:
        return await __common_key_generation(connection=ksid, size=size, relay=False)
    else:
        first: Final[bool] = await dbms_first_kme(ksid=ksid)
        last: Final[bool] = await dbms_last_kme(ksid=ksid)
        if not last:
            logging.getLogger().info("dbms_generate_key")
            link = await __get_link_on_db_by_companion(companion=ksid.kme_dst)
            key_for_sae: Final[Key] = await __common_key_generation(
                connection=ksid, size=size, relay=True, link_id=link.link_id
            )
            if first:
                return key_for_sae, ksid.kme_dst
            else:
                return None, ksid.kme_dst
        return None


async def dbms_save_relayed_key(ksid: UUID, key: Key) -> None:
    """Saves the key to relay the key of a Ksid."""
    logging.getLogger().info("INFO saving relayed key")
    await orm.RelayedKey.objects.create(key_id=key.key_ID, key=key.key, ksid=ksid)


async def dbms_get_next_kme(ksid_id: UUID) -> UUID:
    """Gets the UUID of the next-hop KME."""
    ksid: Final[orm.Ksid] = await get_ksid_on_db(ksid=ksid_id)
    return ksid.kme_dst


async def dbms_last_kme(ksid: orm.Ksid) -> bool:
    """Checks if this KME is the last one hop for the Ksid."""
    last: bool = await orm.Sae.objects.filter(sae_id=ksid.dst).exists()
    return last


async def dbms_first_kme(ksid: orm.Ksid) -> bool:
    """Checks if this KME is the first one hop for the Ksid."""
    first: bool = await orm.Sae.objects.filter(sae_id=ksid.src).exists()
    return first


async def dbms_is_relay(ksid_id: UUID) -> bool:
    """Checks if the Ksid needs the key relay."""
    ksid: Final[orm.Ksid] = await get_ksid_on_db(ksid=ksid_id)
    return ksid.relay


async def __get_block_by_id(block_id: UUID) -> orm.Block:
    """Gets Block with given block_id."""
    try:
        b: orm.Block = await orm.Block.objects.get(block_id=block_id)
        return b
    except NoMatch:
        raise BlockNotFound()


@dataclass(frozen=True, slots=True)
class Instruction:
    """An instruction on how to retrieve key material from a block.

    'start' and 'end' works like for function range(): 'start' is included,
    'end' excluded.
    """

    block_id: UUID
    start: int
    end: int

    def __post_init__(self) -> None:
        if self.start >= self.end:
            raise ValueError(
                f"Instruction for block {self.block_id} has start "
                f"{self.start} >= end {self.end}"
            )


@dataclass(frozen=True, slots=True)
class Block:
    """A block of random bits."""

    time: int
    id: UUID
    key: tuple[int, ...]
    link_id: UUID


async def create_from_qcs_block(qcs_block: Block) -> None:
    # logging.getLogger().info("INFO saving block received by qc")
    await orm.Block.objects.create(
        link_id=qcs_block.link_id,
        block_id=qcs_block.id,
        material=qcs_block.key,
        timestamp=qcs_block.time,
        available_bits=len(qcs_block.key),
    )


async def __pop_block(link_id: UUID) -> orm.Block | None:
    """Retrieves a block from the database, removing it from there.

    This function exploits an async lock, because it has to ensure that the database
    does not return the very same block to multiple requests, before deleting that
    block from the database. The behaviour of pick_block() has to be similar to the
    one of list.pop() or Queue.get_nowait()."""
    logging.getLogger().info(f"INFO pop block to generate key")
    async with lock_blocks:
        b: orm.Block = (
            await orm.Block.objects.filter(
                available_bits__gt=0, link_id=link_id
            ).filter(
                timestamp__gt=now() - Config.TTL
            ).first()
        )
        return b


async def update_available_bits(block_id: UUID, used: int) -> None:
    logging.getLogger().info("INFO updating available bits")
    async with lock_blocks:
        block: orm.Block = await __get_block_by_id(block_id=block_id)
        avb = block.available_bits - used
        in_use = block.in_use
        in_use += 1
        await block.update(available_bits=avb, in_use=in_use)


async def __get_randbits(req_bitlength: int, link_id: UUID) -> tuple[list[int], list[Instruction]]:
    """Asks the quantum channel for new blocks.

    If sd_qkd_node does not have a sufficient number of random bits locally, it is forced to
    communicate with the quantum channel, asking for such bits.
    """
    logging.getLogger().info(f"INFO getting rand bits")
    key_material: list[int] = []
    instructions: list[Instruction] = []

    while (diff := req_bitlength - bit_length(key_material)) > 0:
        b: orm.Block | None = await __pop_block(link_id=link_id)

        if b is None:
            raise BlockNotFound()

        start = len(b.material) - b.available_bits

        if bit_length(b.material[start:]) > diff:
            end = start + diff // 8
        else:
            end = len(b.material)
        in_use = b.in_use
        in_use += 1
        await b.update(available_bits=len(b.material) - end, in_use=in_use)

        link: orm.Link = await orm.Link.objects.get(link_id=link_id)

        companion_kme_addr: str = await dbms_get_kme_address(dst=link.companion)
        await kme_update_block(addr=companion_kme_addr, block_id=b.block_id, used=end - start)

        instructions.append(Instruction(b.block_id, start, end))
        key_material.extend(b.material[start:end])

    return key_material, instructions


async def __generate_key_material(req_bitlength: int, link_id: UUID) -> tuple[str, object]:
    """
    Returns key_material encoded as a base64 string, with the 'req_bitlength'
    requested. Alongside the key material, the instructions to re-build it,
    given the exploited blocks, is returned. These instructions have to be
    stored inside the database shared between communicating KMEs.
    """
    logging.getLogger().info(f"INFO generating key material")
    assert req_bitlength % 8 == 0

    key_material, instructions = await __get_randbits(req_bitlength=req_bitlength, link_id=link_id)

    return collectionint_to_b64(key_material), dump(instructions)


async def __retrieve_key_material(json_instructions: object) -> str:
    """
    Returns the key material re-created based on the given instructions.
    """
    logging.getLogger().info("INFO retrieve key material")
    key_material_ints: list[int] = []

    instructions = load(json_instructions, tuple[Instruction, ...])

    async with lock_blocks:
        for i in instructions:
            b = await __get_block_by_id(block_id=i.block_id)
            in_use = b.in_use
            in_use -= 1
            await b.update(in_use=in_use)
            key_material_ints.extend(b.material[i.start: i.end])

    return collectionint_to_b64(key_material_ints)


async def dbms_save_ksid(ksid: orm.Ksid) -> None:
    """Saves the new Ksid received by the SDN Controller."""
    await orm.Ksid.objects.create(
        src=ksid.src, dst=ksid.dst, kme_src=ksid.kme_src, kme_dst=ksid.kme_dst,
        qos=ksid.qos, ksid=ksid.ksid, relay=ksid.relay
    )


async def dbms_delete_ksid(ksid_to_del: orm.Ksid) -> tuple[bool, bool, str]:
    """Deletes the Ksid when the connection is closed."""
    first: bool = await dbms_first_kme(ksid=ksid_to_del)
    last: bool = await dbms_last_kme(ksid=ksid_to_del)
    next_kme_addr: str = ""
    if not last:
        next_kme_addr = await dbms_get_kme_address(dst=ksid_to_del.kme_dst)
    if first or last:
        await __delete_saes((ksid_to_del.src, ksid_to_del.dst))
    await ksid_to_del.delete()
    return first, last, next_kme_addr


async def dbms_save_sae(sae_id: UUID, port: int, ip: str = "127.0.0.1") -> None:
    """Saves the SAE that requests a connection."""
    await orm.Sae.objects.get_or_create(
        sae_id=sae_id, ip=ip, port=port, defaults={"sae_id": sae_id, "ip": ip, "port": port}
    )


async def __delete_saes(saes: tuple[UUID, UUID]) -> None:
    """Deletes the SAE when it closes the connection and has no other connections active."""
    active_ksids_src1: Final[list[orm.Ksid]] = await orm.Ksid.objects.filter(src=saes[0]).all()
    active_ksids_src2: Final[list[orm.Ksid]] = await orm.Ksid.objects.filter(dst=saes[0]).all()
    active_ksids_dst1: Final[list[orm.Ksid]] = await orm.Ksid.objects.filter(src=saes[1]).all()
    active_ksids_dst2: Final[list[orm.Ksid]] = await orm.Ksid.objects.filter(dst=saes[1]).all()
    if len(active_ksids_src1) + len(active_ksids_src2) == 1:
        await orm.Sae.objects.filter(sae_id=saes[0]).delete()
    if len(active_ksids_dst1) + len(active_ksids_dst2) == 1:
        await orm.Sae.objects.filter(sae_id=saes[1]).delete()


async def dbms_get_sae_address(sae_id: UUID) -> tuple[str, bool]:
    """Gets the address of a SAE if exists."""
    try:
        sae: Final[orm.Sae] = await orm.Sae.objects.get(sae_id=sae_id)
    except NoMatch:
        return "", False
    return f"http://{sae.ip}:{sae.port}", True


async def dbms_get_kme_address(dst: UUID) -> str:
    """Gets the address of the companion KME on the QC."""
    link: Final[orm.Link] = await __get_link_on_db_by_companion(companion=dst)
    return link.addr


async def dbms_save_link(link_id: UUID, ttl: int, rate: float) -> bool:
    """Saves the link when the KME receives blocks from it."""
    link, created = await orm.Link.objects.get_or_create(
        link_id=link_id, defaults={"link_id": link_id, "ttl": ttl, "rate": rate}
    )
    if not created:
        await link.update(rate=rate)
    return created


async def dbms_update_link(link_id: UUID, **kwargs) -> None:
    """Updates the link info received by the SDN Controller about the companion KME."""
    await orm.Link.objects.filter(link_id=link_id).update(**kwargs)
    logging.getLogger().info(f"Link {link_id}, {kwargs}")
