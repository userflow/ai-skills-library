---
name: install-react-native-with-ai
description: Installs @userflow-tech/react-native into an Expo or bare React Native app, including Expo Router and React Navigation. Default install is init(), identify() after sign-in, reset() on logout, UserflowProvider, and screen tracking. Use when someone wants to install Userflow in a React Native, Expo, Expo Router, or React Navigation app. Not for web apps or Userflow.js — those use install-with-ai.
metadata:
  author: userflow
  version: "1.0"
---

# Userflow React Native Installation

This skill installs `@userflow-tech/react-native` correctly and minimally. The install changes which users get identified, which directly affects the customer's Monthly Active User (MAU) count and bill — so follow the core rules below exactly. Userflow counts MAU per user ID, so one user identified on web and mobile, or on several devices, counts once. When the customer already identifies that user from a web Userflow.js install, pass the same user ID to `identify()` here.

**AGENTS.md convention:** Append a "Userflow installation" section to the project's AGENTS.md (or CLAUDE.md, if that is the file the project keeps agent notes in; update both when both exist) recording: package manager, the file where `init()` lives, the file(s) where `identify()` and `reset()` live, where `UserflowProvider` and screen tracking are mounted, the client-token source, the `scheme_id`, and the user-ID field used. Update or append — never overwrite the file or unrelated sections.

## Scope

Install only, for a new or existing React Native codebase. The default install is `init()` + `identify()` + `reset()` + `UserflowProvider` + screen tracking. Verifying an existing install and recommending attributes are out of scope.

If `package.json` has neither `react-native` nor `expo`, this is not a React Native app. Stop and use `install-with-ai`. Never install `userflow.js` here, and never install `@userflow-tech/react-native` into a web app.

## Core Rules (non-negotiable — apply throughout)

1. **Authenticated users only.** Call `identify()` only after sign-in, and again on launches where a user is already signed in. Call `reset()` on logout. Do not call `identifyAnonymous()` on a default install — anonymous users count toward MAU and can cause overages.
2. **Keep it simple.** The default install is the five pieces in Scope. Babel plugin, `identifyAnonymous()`, `group()`, `track()`, and identity verification are Advanced — add one only when the customer asks.
3. **Native modules need a native rebuild.** A Metro reload does not link native modules or URL schemes. Expo Go cannot load this SDK. Use a development build (`npx expo run:ios` / `npx expo run:android`) or a prebuilt bare app.
4. **Tokens.**
   - The client token is `ct_...`, one per environment, from the dashboard (Settings → Environments). Wire it through the app's existing env config.
   - An `esk_...` value is Userflow's identity verification secret key. It is used only on the customer's backend to sign user IDs, and it must never appear in the app, the repo, or the chat.
   - Never invent a token, a `scheme_id`, or a placeholder such as `YOUR_TOKEN` or `ct_...` left in source.
5. **Never initialize twice.** If `@userflow-tech/react-native` is already initialized, point to that `init()` and stop. Do not add a second one.
6. **No destructive or upgrade commands without an explicit yes.** That includes `expo prebuild --clean`, deleting `ios/` or `android/`, and upgrading Expo or React Native.
7. **Ask, don't guess,** for the `scheme_id`, the client token, where sign-in and logout happen, and which field is the user id.
8. **One SDK: `@userflow-tech/react-native`.** Never install `userflow.js` or add a `js.userflow.com` script tag. Never load Userflow.js inside `react-native-webview`, and never call the web API (`userflow.init(token)`, `window.userflow`). The SDK's WebView peer exists for its own banners and Evaluate JavaScript actions, not to host Userflow.js. Installation trouble is never a reason to change SDKs: `ERESOLVE`, "not linked" warnings, Expo Go, `pod install` failures. Fix it through these steps and [troubleshooting.md](https://unpkg.com/@userflow-tech/react-native/docs/troubleshooting.md), or stop and report. See "If installation goes wrong, do not switch to the web SDK".

After the package is installed, read `node_modules/@userflow-tech/react-native/README.md` and its `docs/` (especially `troubleshooting.md`, `deep-linking.md`, and `identity-verification.md`) and follow them. They match the installed version. The same pages are public: [npm package](https://www.npmjs.com/package/@userflow-tech/react-native), [troubleshooting.md](https://unpkg.com/@userflow-tech/react-native/docs/troubleshooting.md), [deep-linking.md](https://unpkg.com/@userflow-tech/react-native/docs/deep-linking.md), and [identity-verification.md](https://unpkg.com/@userflow-tech/react-native/docs/identity-verification.md). Do not quote warning strings from memory; search logs for the `[Userflow]` prefix.

---

## Step 1 — Analyze the project

Inspect before asking, and determine:

| Read | Determine |
|---|---|
| `package.json` | Expo SDK and React Native versions; `expo-router` or `@react-navigation/native`; whether `@userflow-tech/react-native` or `userflow.js` is already installed; `react-native-safe-area-context`; a `test` script (Jest). If `userflow.js` is in this app, follow rule 8 and "If installation goes wrong, do not switch to the web SDK". The SDK requires React Native 0.76 or later (`react-native-view-shot` 5.x does not install below that). If this app is older, stop and say so. Do not upgrade React Native unless the developer explicitly agrees (rule 6). The SDK is tested up to Expo SDK 57. Expo SDK 58 and later bundle `react-native-webview` 14 and `react-native-view-shot` 6, which are outside the SDK's peer ranges. On Expo SDK 58 or later, tell the developer that version is not supported yet and stop. Do not force older WebView or view-shot versions onto it. |
| Lockfile and `.yarnrc.yml` | npm, Yarn 2+, or pnpm |
| `app.json` / `app.config.*`, `ios/`, `android/`, `babel.config.js` | Expo or bare; an existing Userflow config plugin; an existing Babel plugin |
| Root layout or `App.tsx`, and the auth code | Where `init()`, `identify()`, `reset()`, and `UserflowProvider` belong; the user-id field |

Confirm once, naming the real stack — e.g. *"Expo SDK 57 with Expo Router; the current user comes from `useAuth()` in `src/auth/AuthProvider.tsx`; the id is `user.id`, the same id the web app already sends to Userflow. I'll init at startup, identify whenever a user is signed in, and reset on sign-out. Correct?"* — then continue. Ask whether that id matches the web install when the customer has one.

No repository access: do not invent paths. Ask for the stack, auth entry points, and user-id field, or switch to the Developer Handoff Spec and stop.

## Step 2 — Install the packages

List every native module in the app's own `package.json`. Expo SDK 53 and older, and bare React Native, do not autolink packages that are only transitive dependencies. Leave out a package the app already lists at a version that satisfies the SDK, so its existing pin is kept.

```bash
# Expo (drop any package the app already lists at a satisfying version)
npx expo install @userflow-tech/react-native @react-native-async-storage/async-storage react-native-view-shot@^5.0.0 react-native-webview

# Bare React Native (same rule)
npm install @userflow-tech/react-native '@react-native-async-storage/async-storage@^2' 'react-native-device-info@<16' 'react-native-view-shot@^5.0.0' 'react-native-webview@>=13.8.0 <14'
cd ios && pod install
```

Keep the version ranges in the bare command. Unpinned, npm picks the latest majors: `react-native-webview` 14 is outside the SDK's range, and npm only warns `ERESOLVE overriding peer dependency` and installs it anyway. AsyncStorage 3 sits next to the SDK's own 2.x copy, which leaves two copies of one native module. Treat an `overriding peer dependency` warning as a failed install. `npx expo install` picks Expo's bundled versions, which fit the SDK's ranges on Expo SDK 53–57.

Use the app's package manager. On Expo SDK 55 and older, unpinned `npx expo install react-native-view-shot` resolves 4.0.3, which does not satisfy `^5.0.0`. If `package.json` already has view-shot below 5, keep `react-native-view-shot@^5.0.0` in the same install command as `@userflow-tech/react-native`. Installing the SDK alone fails with `ERESOLVE`. The two lines that matter are `Found: react-native-view-shot@4.0.3` and `peer react-native-view-shot@"^5.0.0" from @userflow-tech/react-native`. Rerun the combined command above. Do not retry with `--force` or `--legacy-peer-deps`; that installs the SDK and leaves 4.0.3 in place. On Expo SDK 55 and older, when `expo doctor` then reports a mismatch, add `"react-native-view-shot"` to `expo.install.exclude` in `package.json`.

`react-native-device-info` is for bare React Native. Expo reads the app version from `expo-constants`.

Install `react-native-safe-area-context` unless the app already depends on it. Without it, banners, flow cards, and Builder bars draw under the status bar and home indicator. Expo Router and React Navigation apps usually have it already; a `SafeAreaProvider` in the tree is not a substitute for the package. Also add `@react-native-community/netinfo` and `expo-secure-store` when the app needs instant reconnect or pairing that survives a restart. In bare React Native, pin these too: `'react-native-safe-area-context@<6'` and `'@react-native-community/netinfo@<13'`.

## Step 3 — Register the deep-link scheme

Ask for the environment's `scheme_id`. It starts with `userflow-` (for example `userflow-v7twv2fw2ja2jaco7kesvowmem`). Reject an environment UUID and the app's own scheme.

Expo, in `app.json` or `app.config.js`:

```json
["@userflow-tech/react-native", { "schemeId": "<scheme_id>" }]
```

`npx expo install` already added a bare `"@userflow-tech/react-native"` entry to `plugins`. Replace that entry with the one above. Never leave both, and never leave the bare one.

Bare React Native: follow `docs/deep-linking.md` inside the installed package ([public copy](https://unpkg.com/@userflow-tech/react-native/docs/deep-linking.md)) for the `Info.plist` and `AndroidManifest.xml` entries.

## Step 4 — init, identify, reset

```tsx
import { Userflow } from '@userflow-tech/react-native';

await Userflow.init({ clientToken }); // once per process; safe to call again with the same options
await Userflow.identify(user.id, { name: user.name, email: user.email });
```

- `init` at startup, before `identify`. A second `init` with different options is ignored until the app restarts. When startup code and the auth code both need it, put the `init` call in one small module that both await.
- `identify` wherever the app learns who the current user is: an auth-state listener or the current-user value from the auth context. Hooking only the sign-in function misses sign-up, demo or magic-link sign-in, and restored sessions. Await `init` first.
- `reset` when a signed-in user signs out.
- Read `clientToken` from the app's env config. One token per environment. A value that does not start with `ct_` is a placeholder: skip `init` for that environment and tell the developer. Never replace it with a guess.
- Log `init` and `identify` failures (for example `console.warn`). Do not swallow them; a failed `init` is the usual reason pairing never starts.

## Step 5 — Mount the provider inside SafeAreaProvider

Expo Router already provides `SafeAreaProvider` above the root layout. Mount the provider there:

```tsx
<UserflowProvider>
  {/* screen tracker, step 6 */}
  <Stack />
</UserflowProvider>
```

React Navigation does not. Wrap the app yourself:

```tsx
<SafeAreaProvider>
  <UserflowProvider>
    {/* WithUserflowReactNavigation, step 6 */}
    <NavigationContainer>{/* navigators */}</NavigationContainer>
  </UserflowProvider>
</SafeAreaProvider>
```

`UserflowProvider` can mount before `init` resolves. Put it once, near the top of the tree, inside `SafeAreaProvider`.

## Step 6 — Screen tracking

- **Expo Router:** render `UserflowExpoRouterScreenTracker` from `@userflow-tech/react-native/expo-router` inside the provider. If that entry exports `redirectSystemPath`, add `app/+native-intent.ts` that re-exports it. Without it, Expo Router navigates on the pairing link: the app jumps to the home screen, or element selection fails with "Can't select this element". Older versions do not export it; follow the installed `docs/deep-linking.md` ([public copy](https://unpkg.com/@userflow-tech/react-native/docs/deep-linking.md)).
- **React Navigation:** wrap the navigator with `WithUserflowReactNavigation`.
- **Anything else:** call `Userflow.updateScreen(name)` (or `useUserflowScreen`) when the screen changes.

## Step 7 — Jest

If the app has Jest, mock the SDK in the Jest setup file so tests do not load native modules. Copy the mock from the Jest section of the installed package README. Include the methods the app calls, and also mock the router entry the app imports (`@userflow-tech/react-native/expo-router` or `/navigation`), with every export the app uses from it. In a TypeScript setup file, type the provider's `children` as `ReactNode` so strict mode passes.

## Step 8 — Verify

You run:

- The app's typecheck.
- The app's tests, if it has them.
- A bundle: `npx expo export --platform ios`, or `react-native bundle` for bare React Native. Delete the output afterwards (`expo export` writes `dist/`).

If the typecheck reports errors from inside `node_modules/@userflow-tech/react-native/src` (a missing `.png` module or `@react-navigation/native`), the installed SDK version is too old for Expo's TypeScript setup. Tell the developer and suggest a newer version. Do not add stub declarations or extra dependencies to the app without their OK.

Then hand the customer the steps you cannot do:

1. Rebuild and launch the native app. A Metro reload is not enough. With Expo, if `ios/` or `android/` already exists, `npx expo run:*` does not re-run prebuild, so the new scheme and native modules never reach the native project. Run `npx expo prebuild` first (never `--clean` without a yes). If those folders are committed and hand-edited, treat the app as bare and check the scheme in `Info.plist` and `AndroidManifest.xml`.
2. Confirm the dev console has no `[Userflow]` setup warning. A complete install stays quiet.
3. In the Builder, open Preview → "Pair a device" and scan the QR code. The app shows a "Preview mode" bar. Then press Preview.

Search device logs for `[Userflow]` if any of those fail, and match the line to `docs/troubleshooting.md` ([public copy](https://unpkg.com/@userflow-tech/react-native/docs/troubleshooting.md)).

## If installation goes wrong, do not switch to the web SDK

`@userflow-tech/react-native` is the SDK for this app. Do not install `userflow.js`, and do not follow the Userflow.js pages on help.userflow.com, because a step failed (rule 8).

- The install and API pages on help.userflow.com describe Userflow.js. Do not apply their code here.
- The server error `Invalid Userflow.js Token` is the backend's name for the client token. It means the `ct_` token is wrong, not that `userflow.js` is needed.
- `window is not defined` or `document is not defined` means web code got into the native bundle. Remove that code; do not add more of it.
- `userflow.js` already present in this app's `package.json` or imports is a leftover from a wrong-SDK attempt. Report it and remove it only with a yes. In a monorepo, leave a separate web app's `userflow.js` alone.
- Expo apps that also build for web: this SDK covers iOS and Android. Adding Userflow to the web build is a separate `install-with-ai` job, done only if the customer asks.

## Step 9 — Document

Add or update the "Userflow installation" section in `AGENTS.md` (or `CLAUDE.md`), as described at the top. Never overwrite the rest of the file.

---

## Developer Handoff Spec

Without repository access, do not write code. Generate `USERFLOW_RN_INSTALL_SPEC.md` containing: how to detect Expo vs bare and the router; the install commands; where `scheme_id` and `clientToken` come from; the `init` / `identify` / `reset` / provider / screen-tracking code with the customer's real user-id field named; the Jest mock note; the core rules; and the Step 8 checklist. The document must stand on its own.

## Advanced — only when the customer asks

- **Babel plugin** (`@userflow-tech/react-native/babel-plugin`). It stamps `nativeID` at build time so elements can be targeted without a `testID`. Jest runs `babel.config.js` too, so the plugin rewrites snapshots unless tests skip it. When the app has snapshot tests, gate it and remove `api.cache(true)` (`api.env` caches per environment; calling `api.cache(true)` first throws `Caching has already been configured`):

  ```js
  module.exports = function (api) {
    const isTest = api.env('test');
    return {
      presets: ['babel-preset-expo'],
      plugins: isTest ? [] : ['@userflow-tech/react-native/babel-plugin'],
    };
  };
  ```

  Then clear the Metro cache (`npx expo start -c`). Generated ids change when labels, sibling order, or file paths change, so codeless selectors have to be re-authored. Prefer `testID` unless the customer asked for the plugin.

- **`identifyAnonymous()`.** Opt-in identification of signed-out users. They count toward MAU. Not a fallback for `identify()`. Requires the customer's explicit consent, and requires AsyncStorage to be linked.
- **Identity verification.** Ask first. The signature is an HMAC-SHA256 of the user id, computed on the customer's backend with the identity verification secret key (`esk_...`), and passed as `identify(id, attrs, { signature })`. Follow the installed `docs/identity-verification.md` ([public copy](https://unpkg.com/@userflow-tech/react-native/docs/identity-verification.md)). The secret never ships in the app.
- **`group()` and `track()`.** `group()` after `identify()`, with a real group id. `track()` only once a user is identified.

## Reference

- Installed `node_modules/@userflow-tech/react-native/README.md` — install, placement, API, Jest. Public copy: [npm package](https://www.npmjs.com/package/@userflow-tech/react-native).
- Installed `docs/troubleshooting.md` — [public copy](https://unpkg.com/@userflow-tech/react-native/docs/troubleshooting.md).
- Installed `docs/deep-linking.md` — [public copy](https://unpkg.com/@userflow-tech/react-native/docs/deep-linking.md).
- Installed `docs/identity-verification.md` — [public copy](https://unpkg.com/@userflow-tech/react-native/docs/identity-verification.md).
- [Identity verification](https://help.userflow.com/docs/identity-verification) — the concept only. The code for this SDK is in `docs/identity-verification.md`.
