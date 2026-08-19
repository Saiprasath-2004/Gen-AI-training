class CostTracker:

    def __init__(self) -> None:
          self.total_cost = 0.0

    def add(
        self,
        cost: float | None,
    ) -> None:
        if cost is not None:
            self.total_cost += cost

    def total(self) -> None:
        return self.total_cost