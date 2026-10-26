# Labrador Puppy – Fabric 1.20.1

Animated Labrador puppy entity (Idle + Walk) using the original 3D mesh (not cubes).

## Build / run
**GitHub Actions:** `.github/workflows/build.yml` builds on every push and uploads the jar as an artifact
(works with or without the Gradle wrapper).

**Optional, recommended:** generate the wrapper once on a machine with Gradle and commit it:
`gradle wrapper --gradle-version 8.10.2` then commit `gradlew`, `gradlew.bat`, `gradle/wrapper/gradle-wrapper.jar`.

Requires **JDK 17**. This project has no Gradle wrapper jar; either
* open the folder in IntelliJ IDEA (it imports the Gradle project), or
* run `gradle wrapper --gradle-version 8.10.2` once (needs a local Gradle), or
* generate a fresh project at https://fabricmc.net/develop/template and copy `src/`, `tools/`,
  and the version lines of `gradle.properties` into it.

Then: `./gradlew runClient` (test) or `./gradlew build` (jar in `build/libs/`).

## In game
* `/summon labrador_puppy:puppy`
* Creative inventory → Spawn Eggs → *Labrador Puppy Spawn Egg*
* Spawns naturally in plains / sunflower plains / meadow / forest (edit `ModEntities.init()`).
* Right-click with a **bone**: heals 2 hearts and shows hearts.

## How the animation works
`PuppyMesh` loads `assets/labrador_puppy/mesh/puppy_mesh.bin` (964 vertices, 14 bones, skin weights).
`PuppyPose` computes the pose every frame from vanilla values (`limbAngle`, `limbDistance`, age,
head yaw/pitch); `PuppyMesh.skin` deforms the vertices on the CPU and `PuppyModel` draws them.
* **Idle** (limbDistance≈0): breathing, head sway, tail wag, ear twitches.
* **Walk** (limbDistance≈1): diagonal trot, knee flex, body bob/roll, harder wag, bouncing ears.
They blend automatically. Tune the constants at the top of `PuppyPose.java`.

## Regenerating the rig
`tools/` has the Python scripts (numpy + Pillow + matplotlib). Edit bone pivots / weights in
`tools/rig.py`, then `cd tools && python3 build_assets.py` (re-installs mesh + texture) and
`python3 preview.py walk 24` / `idle 28` for GIF previews. Bone order in `rig.py` must match the
constants in `PuppyPose.java`.

See `docs/preview_walk.gif` and `docs/preview_idle.gif`.
