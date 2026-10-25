"""Pure helpers used by training loops and their focused tests."""


def update_best_metric(current_metric, best_metric):
    """Return whether current_metric is best and the checkpoint metric to save."""
    if current_metric > best_metric:
        return True, current_metric
    return False, best_metric
