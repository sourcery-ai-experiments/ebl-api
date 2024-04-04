import pydash
from marshmallow import Schema, fields, post_load, post_dump
from ebl.schemas import ValueEnumField
from ebl.fragmentarium.domain.colophon import (
    ColophonStatus,
    ColophonType,
    ColophonOwnership,
    NameAttestation,
    ProvenanceAttestation,
    IndividualAttestation,
    IndividualType,
    Colophon,
)
from ebl.common.domain.provenance import Provenance


class NameAttestationSchema(Schema):
    value = fields.String(allow_none=True)
    is_broken = fields.Boolean(data_key="isBroken", allow_none=True)
    is_uncertain = fields.Boolean(data_key="isUncertain", allow_none=True)

    @post_load
    def make_name_attestation(self, data, **kwargs) -> NameAttestation:
        return NameAttestation(**data)

    @post_dump
    def filter_none(self, data, **kwargs) -> dict:
        return pydash.omit_by(data, pydash.is_none)


class ProvenanceAttestationSchema(Schema):
    value = fields.String(required=False, load_default=None)
    is_broken = fields.Boolean(data_key="isBroken", allow_none=True)
    is_uncertain = fields.Boolean(data_key="isUncertain", allow_none=True)

    @post_load
    def make_provenance_attestation(self, data, **kwargs) -> ProvenanceAttestation:
        data["value"] = Provenance[data["value"].split(".")[1]]
        return ProvenanceAttestation(**data)

    @post_dump
    def filter_none(self, data, **kwargs) -> dict:
        return pydash.omit_by(data, pydash.is_none)


class ColophonStatusSchema(Schema):
    value = ValueEnumField(ColophonStatus, allow_none=True)
    is_broken = fields.Boolean(data_key="isBroken", allow_none=True)
    is_uncertain = fields.Boolean(data_key="isUncertain", allow_none=True)

    @post_load
    def make_colophon_status(self, data, **kwargs) -> ColophonStatus:
        return ColophonStatus(**data)

    @post_dump
    def filter_none(self, data, **kwargs) -> dict:
        return pydash.omit_by(data, pydash.is_none)


class IndividualAttestationSchema(Schema):
    name = fields.Nested(NameAttestationSchema, allow_none=True)
    son_of = fields.Nested(NameAttestationSchema, allow_none=True, data_key="sonOf")
    grandson_of = fields.Nested(
        NameAttestationSchema, allow_none=True, data_key="grandsonOf"
    )
    family = fields.Nested(NameAttestationSchema, allow_none=True)
    native_of = fields.Nested(
        ProvenanceAttestationSchema, allow_none=True, data_key="nativeOf"
    )
    type = ValueEnumField(IndividualType, allow_none=True)

    @post_load
    def make_individual_attestation(self, data, **kwargs) -> IndividualAttestation:
        return IndividualAttestation(**data)

    @post_dump
    def filter_none(self, data, **kwargs):
        return pydash.omit_by(data, pydash.is_none)


class ColophonSchema(Schema):
    colophon_status = ValueEnumField(
        ColophonStatus, allow_none=True, data_key="colophonStatus"
    )
    colophon_ownership = ValueEnumField(
        ColophonOwnership, allow_none=True, data_key="colophonOwnership"
    )
    colophon_types = fields.List(
        ValueEnumField(ColophonType), allow_none=True, data_key="colophonTypes"
    )
    original_from = fields.Nested(
        ProvenanceAttestationSchema, allow_none=True, data_key="originalFrom"
    )
    written_in = fields.Nested(
        ProvenanceAttestationSchema, allow_none=True, data_key="writtenIn"
    )
    notes_to_scribal_process = fields.String(
        allow_none=True, data_key="notesToScribalProcess"
    )
    individuals = fields.List(
        fields.Nested(IndividualAttestationSchema), allow_none=True
    )

    @post_load
    def make_colophon(self, data, **kwargs) -> Colophon:
        return Colophon(**data)

    @post_dump
    def filter_none(self, data, **kwargs) -> dict:
        return pydash.omit_by(data, pydash.is_none)
