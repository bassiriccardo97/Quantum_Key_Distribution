from uuid import UUID


class Link:
    def __init__(self, bits: int) -> None:
        self.interval = 5
        self.rate = bits / self.interval
        self.periods = 10
        self.count = 1
        self.alpha = 0.9    # Gives more relevance to last data

    def add_bits(self, bits: int) -> bool:
        self.count += 1
        self.__ewma(bits)
        if self.count == self.periods:
            self.count = 0
            return True
        return False

    def __ewma(self, bits: int) -> None:
        self.rate = (bits / self.interval) * self.alpha + (1 - self.alpha) * self.rate


links: dict[UUID, Link] = {}


def update_rate(link_id: UUID, received_bytes: int) -> tuple[Link, bool]:
    update = False
    bits = received_bytes * 8
    try:
        update = links[link_id].add_bits(bits)
    except KeyError:
        links[link_id] = Link(bits)
    finally:
        return links[link_id], update
