import argparse
import asyncio
import json
import random
import time


class GroundStation(asyncio.DatagramProtocol):
    def __init__(self, expected):
        self.expected = expected
        self.received = {}
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        packet = json.loads(data.decode())
        agent = packet["agent_id"]
        self.received.setdefault(agent, []).append(packet["seq"])


async def run(args):
    loop = asyncio.get_running_loop()
    station = GroundStation(args.agents)
    transport, _ = await loop.create_datagram_endpoint(
        lambda: station, local_addr=("127.0.0.1", args.station_port)
    )
    rng = random.Random(args.seed)

    async def vehicle(agent_id):
        vehicle_transport, protocol = await loop.create_datagram_endpoint(
            asyncio.DatagramProtocol, local_addr=("127.0.0.1", 0)
        )
        del protocol
        try:
            seq = 0
            started = time.monotonic()
            while time.monotonic() - started < args.duration:
                seq += 1
                packet = {
                    "agent_id": agent_id,
                    "seq": seq,
                    "timestamp": round(time.time(), 3),
                    "position": [round(agent_id * 2 + seq * 0.02, 3), agent_id, 10.0],
                    "velocity": [0.02, 0.0, 0.0],
                    "battery": round(100 - seq * 0.12, 2),
                }
                if rng.random() >= args.drop_rate:
                    vehicle_transport.sendto(
                        json.dumps(packet).encode(), ("127.0.0.1", args.station_port)
                    )
                await asyncio.sleep(1 / args.rate)
        finally:
            vehicle_transport.close()

    await asyncio.gather(*(vehicle(i) for i in range(args.agents)))
    await asyncio.sleep(0.05)
    transport.close()
    for agent in range(args.agents):
        seqs = station.received.get(agent, [])
        expected = max(seqs, default=0)
        missing = expected - len(set(seqs))
        print(f"UAV {agent}: received={len(seqs):3d} missing={missing:3d} last_seq={expected:3d}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agents", type=int, default=6)
    parser.add_argument("--duration", type=float, default=8)
    parser.add_argument("--rate", type=float, default=10)
    parser.add_argument("--drop-rate", type=float, default=0.05)
    parser.add_argument("--station-port", type=int, default=16000)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
