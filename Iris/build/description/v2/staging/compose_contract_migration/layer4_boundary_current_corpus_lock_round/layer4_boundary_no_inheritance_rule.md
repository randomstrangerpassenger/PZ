# Layer4 Boundary No-Inheritance Rule

Prior Layer4 zero-count closeout is not inherited as a current measurement result.

This corpus-lock round does not calculate a LAYER4_ABSORPTION_CONFIRMED current count.

An empty current_measurement_corpus set would not be equivalent to current count 0.

Any current count must be produced by a separate downstream remeasurement round that consumes layer4_boundary_current_corpus_manifest.json or layer4_corpus_partition.json.
