# PERIOD image identifier

Checked 2026-11-13 against Docker Hub and the local engine.

| Identifier | Value |
|---|---|
| Local image ID (`docker image inspect period:latest`) | `sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc` |
| Registry manifest digest for `wcventure/period:stable` | `sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc` |

The registry digest is the `docker-content-digest` header from `GET https://registry-1.docker.io/v2/wcventure/period/manifests/stable` using `Accept: application/vnd.docker.distribution.manifest.v2+json`. It is the same string as the local image ID. It is a pullable digest, not only a local label:

```bash
docker pull wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc
```

The image contains Git commit `b6f72a7b06d01ffa7114b640312873ec2578a5ea`. GitHub commit `cb8deb9a176e5bb292d70d46557dd61dc0e98069` changes only documentation.

Pull command if the digest is unavailable: `docker pull wcventure/period:stable`, then check that `docker image inspect` reports this image ID. The Dockerfile in that commit can rebuild the image; the pre-built image is the one used for these runs.
