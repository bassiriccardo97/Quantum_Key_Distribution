from uuid import UUID


class Link:
    def __init__(self, bits: int) -> None:
        self.interval = 1
        self.rate = round(bits / self.interval, 2)
        self.alpha = 0.1    # Gives more relevance to last data

    def add_bits(self, bits: int) -> None:
        self.__ewma(bits)

    def __ewma(self, bits: int) -> None:
        self.rate = round((bits / self.interval) * self.alpha + (1 - self.alpha) * self.rate, 2)


links: dict[UUID, Link] = {}


def update_rate(link_id: UUID, received_bytes: int) -> tuple[Link, bool]:
    update = False
    bits = received_bytes * 8
    try:
        links[link_id].add_bits(bits)
        update = True
    except KeyError:
        links[link_id] = Link(bits)
    finally:
        return links[link_id], update
