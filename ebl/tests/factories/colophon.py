import factory
import random
from ebl.fragmentarium.domain.colophon import (
    ColophonStatus,
    ColophonType,
    NameAttestation,
    ProvenanceAttestation,
    IndividualAttestation,
    Colophon,
    IndividualType,
    ColophonOwnership,
)
from ebl.common.domain.provenance import Provenance


class NameAttestationFactory(factory.Factory):
    class Meta:
        model = NameAttestation

    value = factory.Faker("word")
    is_broken = factory.Faker("boolean")
    is_uncertain = factory.Faker("boolean")


class ProvenanceAttestationFactory(factory.Factory):
    class Meta:
        model = ProvenanceAttestation

    value = factory.fuzzy.FuzzyChoice([p for p in Provenance])
    is_broken = factory.Faker("boolean")
    is_uncertain = factory.Faker("boolean")


class IndividualAttestationFactory(factory.Factory):
    class Meta:
        model = IndividualAttestation

    name = factory.SubFactory(NameAttestationFactory)
    son_of = factory.SubFactory(NameAttestationFactory)
    grandson_of = factory.SubFactory(NameAttestationFactory)
    family = factory.SubFactory(NameAttestationFactory)
    native_of = factory.SubFactory(ProvenanceAttestationFactory)
    type = factory.fuzzy.FuzzyChoice([t for t in IndividualType])


class ColophonFactory(factory.Factory):
    class Meta:
        model = Colophon

    colophon_status = factory.fuzzy.FuzzyChoice([cs for cs in ColophonStatus])
    colophon_ownership = factory.fuzzy.FuzzyChoice([co for co in ColophonOwnership])
    colophon_types = factory.List(
        [
            factory.fuzzy.FuzzyChoice([ct for ct in ColophonType])
            for _ in range(random.randint(1, 3))
        ]
    )
    original_from = factory.SubFactory(ProvenanceAttestationFactory)
    written_in = factory.SubFactory(ProvenanceAttestationFactory)
    notes_to_scribal_process = factory.Faker("sentence")
    individuals = factory.List(
        [
            factory.SubFactory(IndividualAttestationFactory)
            for _ in range(random.randint(0, 2))
        ]
    )
