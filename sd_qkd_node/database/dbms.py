"""Manage everything about database of the SD-QKD Node."""
import asyncio
import logging

from dataclasses import dataclass
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

lock_links = asyncio.Lock()
lock_blocks = asyncio.Lock()
lock = asyncio.Lock()


# OK
async def __clear() -> None:
    """Deletes unnecessary blocks from database.

    A block is deleted if it satisfies at least one of the following conditions:
    - It reached Config.TTL, that is: it is considered too old in order to be used for key generation.
    - Its number of available bits is 0: the block has been completely exploited for key generation.
    """
    logging.getLogger().info("INFO clearing local db from old blocks")
    await orm.Block.objects.filter(available_bits__exact=0, in_use=0).delete()
    await orm.Block.objects.filter(timestamp__lte=now() - Config.TTL, in_use=0).delete()


# ---------------- NEW GET KEY-------------------
# OK
async def __get_key_on_db(key_id: UUID | None, ksid: UUID | None, link_id: UUID | None) -> orm.Key:
    key: orm.Key | None = None
    error: str = ""
    try:
        if key_id is not None:
            # key asked by slave sae with dec_keys
            error = f"...{str(key_id)[25:]}"
            logging.getLogger().info(f"retrieving key on db for ksid ...{str(ksid)[25:]} [__get_key_on_db]")
            key = await orm.Key.objects.get(key_id=key_id)
            logging.getLogger().info(f"retrieved key on db for ksid ...{str(ksid)[25:]} [__get_key_on_db]")
        if link_id is not None:
            # key relay
            error = f"for Ksid ...{str(ksid)[25:]}"
            logging.getLogger().info(f"retrieving key on db for ksid ...{str(ksid)[25:]} [__get_key_on_db]")
            key = await orm.Key.objects.filter(ksid=ksid, link_id=link_id).first()
            logging.getLogger().info(f"retrieved key on db for ksid ...{str(ksid)[25:]} [__get_key_on_db]")
        return key
    except NoMatch:
        raise HTTPException(
            status_code=500,
            detail=f"Key not found on db {error}"
        )


# OK
async def __retrieve_key_direct(key_id: UUID) -> Key:
    orm_key: orm.Key = await __get_key_on_db(key_id=key_id, ksid=None, link_id=None)
    if orm_key is not None:
        logging.getLogger().info(f"deleting key ...{str(key_id)[25:]} [__retrieve_key_direct]")
        await orm_key.delete()
        logging.getLogger().info(f"deleted key ...{str(key_id)[25:]} [__retrieve_key_direct]")
        try:
            key_material = await __retrieve_key_material(json_instructions=orm_key.instructions)
        except BlockNotFound:
            raise BlockNotFound()
        return Key(key_id, key_material)
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Direct key not found ...{str(key_id)[25:]}"
        )


# OK
async def dbms_get_key_direct(key_id: UUID) -> KeyContainer:
    await __clear()
    try:
        return KeyContainer(keys=tuple([await __retrieve_key_direct(key_id=key_id)]))
    except BlockNotFound:
        raise HTTPException(
            status_code=500,
            detail=f"Failed retrieving key."
        )


# OK
async def __get_link_by_companion(companion: UUID) -> orm.Link:
    logging.getLogger().info("INFO getting link by companion")
    async with lock_links:
        try:
            link = await orm.Link.objects.get(companion=companion)
            return link
        except NoMatch:
            raise HTTPException(
                status_code=500,
                detail=f"on {Config.SAE_TO_KME_PORT} Link with KME companion ...{str(companion)[25:]} not found"
            )


# OK
async def dbms_get_decryption_key(ksid: orm.Ksid) -> Key:
    link: orm.Link = await __get_link_by_companion(companion=ksid.kme_src)
    orm_key: orm.Key = await __get_key_on_db(ksid=ksid.ksid, link_id=link.link_id, key_id=None)
    if orm_key is not None:
        logging.getLogger().info(f"deleting key on db for ksid ...{str(ksid.ksid)[25:]} [dbms_get_decryption_key]")
        await orm_key.delete()
        logging.getLogger().info(f"deleted key on db for ksid ...{str(ksid.ksid)[25:]} [dbms_get_decryption_key]")
        key_material = await __retrieve_key_material(json_instructions=orm_key.instructions)
        return Key(orm_key.key_id, key_material)
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Decryption key not found for Ksid ...{str(ksid.ksid)[25:]}"
        )


# OK
async def __retrieve_key_relay(key_id: UUID) -> Key:
    """Gets key material for relay connection."""
    key: orm.LocalKey = await orm.LocalKey.objects.filter(key_id=key_id).first()
    if key is None:
        raise HTTPException(
            status_code=500,
            detail=f"Relay key not found ...{str(key_id)[25:]}"
        )
    else:
        await key.delete()
        return Key(key_ID=key_id, key=key.key)


# OK
async def dbms_get_relayed_key(key_id: UUID) -> KeyContainer:
    await __clear()
    return KeyContainer(keys=tuple([await __retrieve_key_relay(key_id=key_id)]))


# OK
async def get_local_key(ksid: UUID) -> Key | None:
    # not relevant which one is returned first
    key: orm.LocalKey = await orm.LocalKey.objects.filter(ksid=ksid).first()
    if key is not None:
        logging.getLogger().info(f"GOT LOCAL KEY {key.key}")
        await key.delete()
        return Key(key_ID=key.key_id, key=key.key)
    else:
        return None

# ---------------- END NEW GET KEY-------------------


# ---------------- NEW KEY GENERATION ----------------

# OK
async def __generate_single_key_direct(size: int, link: orm.Link, ksid: UUID, local: bool) -> Key:
    key_id: UUID = uuid4()
    key_material, json_instructions = await __generate_key_material(req_bitlength=size, link=link, use=True)
    logging.getLogger().info(f"creating key on db for ksid ...{str(ksid)[25:]} [__generate_single_key_direct]")
    await orm.Key.objects.create(key_id=key_id, ksid=ksid, instructions=json_instructions, relay=False)
    logging.getLogger().info(f"created key on db for ksid ...{str(ksid)[25:]} [__generate_single_key_direct]")
    if local:
        # Store also locally since it is a future key, to be returned without retrieving instructions
        await orm.LocalKey.objects.create(key_id=key_id, ksid=ksid, key=key_material, relay=False)
    return Key(key_ID=key_id, key=key_material)


# OK
async def dbms_generate_keys_direct(ksid: orm.Ksid, size: int, local: bool) -> Key:
    link: orm.Link = await __get_link_by_companion(companion=ksid.kme_dst)
    transaction = await shared_db.transaction()
    async with lock:
        try:
            if local:
                for _ in range(Config.KEYS_AHEAD):
                    # generates future keys storing them both on local db and shared db
                    await __generate_single_key_direct(size=size, ksid=ksid.ksid, link=link, local=True)
            # the last key generated is the one returned immediately, thus it is stored only on the shared db
            key = await __generate_single_key_direct(size=size, ksid=ksid.ksid, link=link, local=False)
        except BlockNotFound:
            await transaction.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Block not found [[...{str(ksid.src)[25:]} -> ...{str(ksid.dst)[25:]}]]"
            )
        except:
            await transaction.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error generating keys for Ksid ...{str(ksid.ksid)[25:]}"
            )
        else:
            await transaction.commit()
            return key


# OK
async def __generate_single_key_relay(size: int, ksid: UUID, link: orm.Link, store: bool) -> Key:
    key_id: UUID = uuid4()
    key_material, json_instructions = await __generate_key_material(req_bitlength=size, link=link, use=False)
    if store:
        # relayed keys are not shared with any KME directly, thus they are stored only locally
        # this is even more true if they are future keys
        await orm.LocalKey.objects.create(key_id=key_id, ksid=ksid, key=key_material, relay=False)
    return Key(key_ID=key_id, key=key_material)


# OK
async def dbms_generate_keys_relay(ksid: orm.Ksid, size: int, local: bool) -> tuple[Key, list[Key]] | Key:
    link: orm.Link = await __get_link_by_companion(companion=ksid.kme_dst)
    future_keys: list[Key] = []
    transaction = await shared_db.transaction()
    async with lock:
        try:
            if local:
                for _ in range(Config.KEYS_AHEAD):
                    future_keys.append(
                        await __generate_single_key_relay(size=size, ksid=ksid.ksid, link=link, store=True)
                    )
                    logging.getLogger().info(f"FUTURE KEY {future_keys[-1].key}")
            # The last generated key is the one immediately returned to the master SAE, thus it is not necessary
            # to store it locally
            key = await __generate_single_key_relay(size=size, ksid=ksid.ksid, link=link, store=False)
        except BlockNotFound:
            await transaction.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Block not found [[...{str(ksid.src)[25:]} -> ...{str(ksid.dst)[25:]}]]"
            )
        except:
            await transaction.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error generating keys for Ksid ...{str(ksid.ksid)[25:]}"
            )
        else:
            await transaction.commit()
            if not local:
                return key
            return key, future_keys


# OK
async def dbms_generate_encryption_key_for_relay(ksid: orm.Ksid, size: int) -> Key:
    link: orm.Link = await __get_link_by_companion(companion=ksid.kme_dst)
    key_id: UUID = uuid4()
    transaction = await shared_db.transaction()
    async with lock:
        try:
            key_material, json_instructions = await __generate_key_material(req_bitlength=size, link=link, use=True)
            logging.getLogger().info(f"creating key on db for ksid ...{str(ksid.ksid)[25:]} [dbms_generate_encryption_key_for_relay]")
            await orm.Key.objects.create(
                key_id=key_id, ksid=ksid.ksid, instructions=json_instructions, relay=True, link_id=link.link_id
            )
            logging.getLogger().info(f"created key on db for ksid ...{str(ksid.ksid)[25:]} [dbms_generate_encryption_key_for_relay]")
        except BlockNotFound:
            await transaction.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Block not found [[...{str(ksid.src)[25:]} -> ...{str(ksid.dst)[25:]}]]"
            )
        except:
            await transaction.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error generating keys for Ksid ...{str(ksid.ksid)[25:]}"
            )
        else:
            await transaction.commit()
            return Key(key_ID=key_id, key=key_material)
            # await orm.Key.objects.filter(ksid=ksid.ksid, link_id=link.link_id).first()


# OK
async def dbms_save_relayed_key(ksid: orm.Ksid, keys: Key) -> None:
    """Saves the key to relay the key of a Ksid."""
    logging.getLogger().info(f"SAVING RELAYED KEY {keys.key}")
    await orm.LocalKey.objects.create(key_id=keys.key_ID, key=keys.key, ksid=ksid.ksid)


# OK
async def dbms_get_encryption_key(ksid: orm.Ksid) -> Key:
    """Saves the key to relay the key of a Ksid."""
    key: orm.LocalKey = await orm.LocalKey.objects.filter(ksid=ksid.ksid).first()
    if key is not None:
        await key.delete()
        return Key(key_ID=key.key_id, key=key.key)
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Encryption key not found"
        )

# ---------------- END NEW KEY GENERATION ----------------


# ---------------- ACTUAL KEY GENERATION/RETRIEVING ----------------

async def __get_block_by_id(block_id: UUID) -> orm.Block:
    """Gets Block with given block_id."""
    try:
        b: orm.Block = await orm.Block.objects.get(block_id=block_id)
        return b
    except NoMatch:
        raise BlockNotFound()
        # raise HTTPException(
        #    status_code=500,
        #    detail="Insufficient key material."
        # )


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


async def __get_randbits(req_bitlength: int, link: orm.Link, use: bool) -> tuple[list[int], list[Instruction]]:
    """Asks the quantum channel for new blocks.

    If sd_qkd_node does not have a sufficient number of random bits locally, it is forced to
    communicate with the quantum channel, asking for such bits.
    """
    logging.getLogger().info(f"INFO getting rand bits")
    key_material: list[int] = []
    instructions: list[Instruction] = []

    while (diff := req_bitlength - bit_length(key_material)) > 0:
        b: orm.Block | None = await __pop_block(link_id=link.link_id)

        if b is None:
            # logging.getLogger().error(f"ERROR run out of blocks.")
            raise BlockNotFound()
            # raise HTTPException(
            #    status_code=500,
            #    detail="Insufficient key material."
            # )

        start = len(b.material) - b.available_bits

        if bit_length(b.material[start:]) > diff:
            end = start + diff // 8
        else:
            end = len(b.material)
        in_use = b.in_use
        if use:
            # 'in_use' is incremented only if it is a direct key, not a relayed one, because the relayed ones are not
            # retrieved by the successive KME, thus 'in_use' would not be decremented, preventing the blocks to be
            # deleted when expired
            in_use += 1
        await b.update(available_bits=len(b.material) - end, in_use=in_use)

        companion_kme_addr: str = await dbms_get_kme_address(dst=link.companion)
        await kme_update_block(addr=companion_kme_addr, block_id=b.block_id, used=end - start)

        instructions.append(Instruction(b.block_id, start, end))
        key_material.extend(b.material[start:end])

    return key_material, instructions


async def __generate_key_material(req_bitlength: int, link: orm.Link, use: bool) -> tuple[str, object]:
    """
    Returns key_material encoded as a base64 string, with the 'req_bitlength'
    requested. Alongside the key material, the instructions to re-build it,
    given the exploited blocks, is returned. These instructions have to be
    stored inside the database shared between communicating KMEs.
    """
    logging.getLogger().info(f"INFO generating key material")
    assert req_bitlength % 8 == 0

    try:
        key_material, instructions = await __get_randbits(req_bitlength=req_bitlength, link=link, use=use)
    except BlockNotFound:
        raise BlockNotFound()
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
            try:
                b = await __get_block_by_id(block_id=i.block_id)
            except BlockNotFound:
                raise BlockNotFound()
            in_use = b.in_use
            in_use -= 1
            await b.update(in_use=in_use)
            key_material_ints.extend(b.material[i.start: i.end])

    return collectionint_to_b64(key_material_ints)

# ---------------- END ACTUAL KEY GENERATION/RETRIEVING ----------------


# KSIDs

# OK
async def dbms_get_ksid(**kwargs) -> orm.Ksid:
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


async def dbms_save_ksid(ksid: orm.Ksid) -> None:
    """Saves the new Ksid received by the SDN Controller."""
    await orm.Ksid.objects.create(
        src=ksid.src, dst=ksid.dst, kme_src=ksid.kme_src, kme_dst=ksid.kme_dst,
        qos=ksid.qos, ksid=ksid.ksid, relay=ksid.relay
    )


async def dbms_delete_ksid(ksid_to_del: orm.Ksid) -> tuple[bool, bool, str]:
    """Deletes the Ksid when the connection is closed."""
    first = ksid_to_del.kme_src == Config.KME_ID
    last = ksid_to_del.kme_dst == Config.KME_ID
    next_kme_addr: str = ""
    if not last:
        next_kme_addr = await dbms_get_kme_address(dst=ksid_to_del.kme_dst)
    # if first or last:
    #    await __delete_saes((ksid_to_del.src, ksid_to_del.dst))
    await ksid_to_del.delete()
    return first, last, next_kme_addr
    # TODO delete local keys not utilized


# LINKs

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
    async with lock_links:
        await orm.Link.objects.filter(link_id=link_id).update(**kwargs)
        logging.getLogger().info(f"Link {link_id}, {kwargs}")


async def dbms_get_kme_address(dst: UUID) -> str:
    """Gets the address of the companion KME on the QC."""
    link: Final[orm.Link] = await __get_link_by_companion(companion=dst)
    return link.addr


@dataclass(frozen=True, slots=True)
class Block:
    """A block of random bits."""

    time: int
    id: UUID
    key: tuple[int, ...]
    link_id: UUID


# called by qcs thread, can't use asyncio.Lock()
async def create_from_qcs_block(qcs_block: Block) -> None:
    # logging.getLogger().info("INFO saving block received by qc")
    await orm.Block.objects.create(
        link_id=qcs_block.link_id,
        block_id=qcs_block.id,
        material=qcs_block.key,
        timestamp=qcs_block.time,
        available_bits=len(qcs_block.key),
    )


# SAEs

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
        saes: list[orm.Sae] = await orm.Sae.objects.all()
        sae: Final[orm.Sae] = await orm.Sae.objects.get(sae_id=sae_id)
    except NoMatch:
        return "", False
    return f"http://{sae.ip}:{sae.port}", True
