"""PANNs construction with an explicit, validated runtime device."""


def load_audio_tagging(device, audio_tagging_cls=None, cuda_available=None):
    device_name = str(device)
    device_kind = device_name.split(":", 1)[0]
    if device_kind not in {"cpu", "cuda"}:
        raise ValueError(
            f"PANNs AudioTagging supports only CPU or CUDA device names, got {device_name!r}"
        )

    if cuda_available is None:
        try:
            import torch
        except ImportError as exc:
            raise RuntimeError("PyTorch is required to check PANNs device availability") from exc
        cuda_available = torch.cuda.is_available()

    if device_kind == "cuda" and not cuda_available:
        raise RuntimeError(
            f"PANNs was configured for {device_name}, but CUDA is unavailable"
        )

    if audio_tagging_cls is None:
        try:
            from panns_inference import AudioTagging
        except ImportError as exc:
            raise RuntimeError(
                "PANNs inference dependency is unavailable; install the project's ML requirements first"
            ) from exc
        audio_tagging_cls = AudioTagging

    try:
        return audio_tagging_cls(device=device_name)
    except Exception as exc:
        raise RuntimeError(
            f"PANNs AudioTagging could not initialize on {device_name}: {exc}"
        ) from exc


def unwrap_panns_model(audio_tagging):
    """Handle both DataParallel CUDA wrappers and unwrapped model instances."""
    model = audio_tagging.model
    return model.module if hasattr(model, "module") else model
