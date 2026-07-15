import random
from typing import Any
from dataclasses import dataclass, field


@dataclass
class AgentGenome:
    agent_id: str
    generation: int = 0
    fitness: float = 0.0
    params: dict = field(default_factory=dict)
    novelty: float = 0.0


class GroupEvolution:
    def __init__(self, population_size: int = 27):
        self.population_size = population_size
        self.generation = 0
        self.population: dict[str, AgentGenome] = {}
        self.history: list[dict] = []
        self.performances: dict[str, list[float]] = {}

    def register_agent(self, agent_id: str, initial_params: dict = None) -> None:
        self.population[agent_id] = AgentGenome(
            agent_id=agent_id,
            params=initial_params or {},
        )
        self.performances[agent_id] = []

    def record_performance(self, agent_id: str, fitness: float) -> None:
        if agent_id in self.performances:
            self.performances[agent_id].append(fitness)
            if len(self.performances[agent_id]) > 100:
                self.performances[agent_id] = self.performances[agent_id][-100:]

        if agent_id in self.population:
            genome = self.population[agent_id]
            recent = self.performances[agent_id][-10:]
            genome.fitness = sum(recent) / len(recent) if recent else 0.0

    def evolve(self) -> dict:
        self.generation += 1
        results = []

        for agent_id, genome in self.population.items():
            recent = self.performances.get(agent_id, [])
            if len(recent) < 5:
                continue

            fitness = genome.fitness
            novelty = self._calculate_novelty(agent_id, genome)

            mutation = random.uniform(0.9, 1.1) if random.random() < 0.1 else 1.0
            genome.novelty = novelty

            results.append({
                "agent_id": agent_id,
                "generation": self.generation,
                "fitness": round(fitness, 4),
                "novelty": round(novelty, 4),
                "mutation_factor": round(mutation, 4),
            })

        self.history.append({
            "generation": self.generation,
            "population_size": len(self.population),
            "avg_fitness": round(sum(r["fitness"] for r in results) / len(results), 4) if results else 0,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        })

        return {"generation": self.generation, "results": results}

    def _calculate_novelty(self, agent_id: str, genome: AgentGenome) -> float:
        recent = self.performances.get(agent_id, [])
        if len(recent) < 2:
            return 0.0
        return abs(recent[-1] - recent[-2]) if len(recent) >= 2 else 0.0

    def get_status(self) -> dict:
        return {
            "current_generation": self.generation,
            "population_size": len(self.population),
            "history_length": len(self.history),
            "top_agents": self._get_top_agents(5),
        }

    def _get_top_agents(self, n: int) -> list[dict]:
        sorted_genomes = sorted(
            self.population.values(),
            key=lambda g: g.fitness,
            reverse=True,
        )
        return [
            {"agent_id": g.agent_id, "fitness": round(g.fitness, 4)}
            for g in sorted_genomes[:n]
        ]
