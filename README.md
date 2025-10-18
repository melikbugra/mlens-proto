# MLens Proto

Protobuf schemas and generated packages for simple, fast experiment tracking. Use the prebuilt packages (npm/PyPI) or generate code for your language of choice.

## What’s inside

- Minimal, pragmatic schema (`mlens.v1`):
  - Experiment and Run metadata
  - Params (string key/value)
  - Scalar metrics (step, timestamp, value)
  - Append-only RunEvent stream (param_set, metric)

File layout:

- `mlens_proto/proto/common.proto`
- `mlens_proto/proto/experiment.proto`
- `mlens_proto/proto/events.proto`

## Install (prebuilt packages)

JavaScript/TypeScript:

```bash
npm i @melikbugra/mlens-proto
```

Python:

```bash
pip install mlens-proto
```

QA (pre-release) builds may be published under the `next` tag for npm and TestPyPI for Python.

## Quick usage

TypeScript:

```ts
import { ExperimentMeta, RunMeta, RunEvent } from '@melikbugra/mlens-proto';

const exp: ExperimentMeta = { experimentId: 'exp-1', name: 'Demo', createdAt: Math.floor(Date.now()/1000) };
```

Python:

```py
from mlens_proto.proto import experiment_pb2 as exp_pb

exp = exp_pb.ExperimentMeta(experiment_id='exp-1', name='Demo', created_at=1700000000)
```

## Generate code yourself

Python:

```bash
python -m pip install grpcio-tools protobuf
python -m grpc_tools.protoc \
  -I mlens_proto/proto \
  --python_out=src \
  mlens_proto/proto/*.proto
```

TypeScript (ts-proto):

```bash
npm i -D ts-proto protobufjs
protoc \
  -I mlens_proto/proto \
  --ts_proto_out=src/gen \
  --ts_proto_opt=esModuleInterop=true,outputServices=none,env=node \
  mlens_proto/proto/*.proto
npm run build
```

## Versioning and CI/CD

- develop → QA:
  - Semantic version bump (no tag), build and publish to TestPyPI and npm with `next` dist-tag (if NPM_TOKEN is provided)
- main → tag:
  - Creates a git tag (semantic version)
- tag → Prod publish:
  - Publishes to PyPI (Trusted Publisher) and npm (latest)

Set up:

- PyPI/TestPyPI Trusted Publisher: Link this repo to PyPI/TestPyPI via OIDC (no tokens needed).
- NPM publish: Add `NPM_TOKEN` (Automation token) to repo secrets.

## License

MIT
