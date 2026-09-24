from __future__ import annotations
from .canonical import digest
from .model import Projection, Residual, Provenance

def make_projection(source_ids, future_family, signature, *, lost_distinctions=(), reconstruction_handle=None):
    body={"source_ids":list(source_ids),"future_family":list(future_family),"signature":list(signature),"lost":list(lost_distinctions)}
    return Projection(digest(body),tuple(source_ids),tuple(future_family),tuple(signature),tuple(lost_distinctions),reconstruction_handle)

def recursively_sufficient(left: Projection, right: Projection, future_results_left, future_results_right) -> bool:
    if left.signature != right.signature: return True
    return tuple(future_results_left)==tuple(future_results_right)

def residual_for_failed_compression(left_id,right_id,projection_id,discriminator,provenance=Provenance()):
    body={"left":left_id,"right":right_id,"projection":projection_id,"discriminator":discriminator}
    return Residual(digest(body),"previously-collapsed states separated by lawful future consequence",(left_id,right_id,projection_id),discriminator,discriminator,provenance)

def deletion_is_consequential(before, after) -> bool:
    return before != after
