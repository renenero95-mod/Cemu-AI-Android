# Build Repo Context
This repo just builds the `Cemu` fork. 
The workflow (`.github/workflows/build.yml`) clones `renenero95-mod/Cemu` (branch `android-port`), applies no patches (already in fork), modifies AppID to `com.cemu.aimod`, and builds with Gradle.
Check the other repo for code context.
