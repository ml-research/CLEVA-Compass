from dataclasses import dataclass


@dataclass
class InnerLevel:
    """Inner CLEVA-Compass level with method attributes."""

    multiple_models: int
    federated: int
    online: int
    open_world: int
    multiple_modalities: int
    active_data_query: int
    task_order_discovery: int
    task_agnostic: int
    episodic_memory: int
    generative: int
    uncertainty: int

    def __iter__(self):
        """
        Defines the iteration order. This needs to be the same order as defined in the
        cleva_template.tex file.
        """
        for item in [
            self.multiple_models,
            self.federated,
            self.online,
            self.open_world,
            self.multiple_modalities,
            self.active_data_query,
            self.task_order_discovery,
            self.task_agnostic,
            self.episodic_memory,
            self.generative,
            self.uncertainty,
        ]:
            yield item


@dataclass
class OuterLevel:
    """Outer CLEVA-Compass level with measurement attributes."""

    compute_time: bool
    mac_operations: bool
    communication: bool
    forgetting: bool
    forward_transfer: bool
    backward_transfer: bool
    openness: bool
    parameters: bool
    memory: bool
    stored_data: bool
    generated_data: bool
    optimization_steps: bool
    per_task_metric: bool
    task_order: bool
    data_per_task: bool

    def __iter__(self):
        """
        Defines the iteration order. This needs to be the same order as defined in the
        cleva_template.tex file.
        """
        for item in [
            self.parameters,
            self.compute_time,
            self.mac_operations,
            self.communication,
            self.forgetting,
            self.forward_transfer,
            self.backward_transfer,
            self.openness,
            self.data_per_task,
            self.task_order,
            self.per_task_metric,
            self.optimization_steps,
            self.generated_data,
            self.stored_data,
            self.memory,
        ]:
            yield item


@dataclass
class CompassEntry:
    """Compass entry containing color, label, and attributes."""

    color: str  # Color, can be one of [magenta, green, blue, orange, cyan, brown]
    label: str  # Legend label
    inner_level: InnerLevel
    outer_level: OuterLevel
