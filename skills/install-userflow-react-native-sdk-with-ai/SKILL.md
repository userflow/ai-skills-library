---
name: install-userflow-react-native-sdk-with-ai
description: Installs @userflow-tech/react-native into an Expo or bare React Native app, including Expo Router and React Navigation. Default install is init(), identify() after sign-in, reset() on logout, UserflowProvider, screen tracking, and the Babel plugin that lets authors select elements on the device. Use when someone wants to install Userflow in a React Native, Expo, Expo Router, or React Navigation app. Not for web apps or Userflow.js — those use install-with-ai.
metadata:
  author: userflow
  version: "1.0"
---

# Userflow React Native Installation

This skill installs `@userflow-tech/react-native` correctly and minimally. The install changes which users get identified, which directly affects the customer's Monthly Active User (MAU) count and bill — so follow the core rules below exactly. Userflow counts MAU per user ID, so one user identified on web and mobile, or on several devices, counts once. When the customer already identifies that user from a web Userflow.js install, pass the same user ID to `identify()` here.

**AGENTS.md convention:** Append a "Userflow installation" section to the project's AGENTS.md (or CLAUDE.md, if that is the file the project keeps agent notes in; update both when both exist) recording: package manager, the file where `init()` lives, the file(s) where `identify()` and `reset()` live (or that the app has no sign-in), where `UserflowProvider` and screen tracking are mounted, the Babel config that loads the plugin, the client-token source, the `scheme_id`, and the user-ID field used. Update or append — never overwrite the file or unrelated sections.

## Scope

Install only, for a new or existing React Native codebase. The default install is `init()` + `identify()` + `reset()` + `UserflowProvider` + screen tracking + the Babel plugin. Verifying an existing install and recommending attributes are out of scope.

If `package.json` has neither `react-native` nor `expo`, this is not a React Native app. Stop and use `install-with-ai`. Never install `userflow.js` here, and never install `@userflow-tech/react-native` into a web app.

## Core Rules (non-negotiable — apply throughout)

1. **Authenticated users only.** Call `identify()` only after sign-in, and again on launches where a user is already signed in. Call `reset()` on logout. Do not call `identifyAnonymous()` on a default install — anonymous users count toward MAU and can cause overages.
2. **Keep it simple.** The default install is the six pieces in Scope. `identifyAnonymous()`, `group()`, `track()`, and identity verification are Advanced — add one only when the customer asks, or, for identity verification, when the environment requires it (Step 1).
3. **Native modules need a native rebuild.** A Metro reload does not link native modules or URL schemes. Expo Go cannot load this SDK. Use a development build (`npx expo run:ios` / `npx expo run:android`) or a prebuilt bare app.
4. **Tokens.**
   - The client token is `ct_...`, one per environment, from the dashboard (Settings → Environments). Wire it through the app's existing env config.
   - An `esk_...` value is Userflow's identity verification secret key. It is used only on the customer's backend to sign user IDs, and it must never appear in the app, the repo, or the chat.
   - Never invent a token, a `scheme_id`, or a placeholder such as `YOUR_TOKEN` or `ct_...` left in source.
5. **Never initialize twice.** If `@userflow-tech/react-native` is already initialized, point to that `init()` and stop. Do not add a second one.
6. **No destructive or upgrade commands without an explicit yes.** That includes `expo prebuild --clean`, deleting `ios/` or `android/`, and upgrading Expo or React Native.
7. **Ask, don't guess,** for the `scheme_id`, the client token, where sign-in and logout happen, and which field is the user id.
8. **One SDK: `@userflow-tech/react-native`.** Never install `userflow.js` or add a `js.userflow.com` script tag. Never load Userflow.js inside `react-native-webview`, and never call the web API (`userflow.init(token)`, `window.userflow`). The SDK's WebView peer exists for its own banners and Evaluate JavaScript actions, not to host Userflow.js. Installation trouble is never a reason to change SDKs: `ERESOLVE`, "not linked" warnings, Expo Go, `pod install` failures. Fix it through these steps and [troubleshooting.md](https://unpkg.com/@userflow-tech/react-native/docs/troubleshooting.md), or stop and report. See "If installation goes wrong, do not switch to the web SDK".

After the package is installed, read `node_modules/@userflow-tech/react-native/README.md` and its `docs/` (especially `troubleshooting.md`, `deep-linking.md`, and `identity-verification.md`) and follow them. They match the installed version. Where they disagree with this skill about view-shot pinning, `app/+native-intent.ts`, or the Babel plugin's Jest config, follow this skill: the 0.4.4 README predates those fixes. The same pages are public: [README.md](https://unpkg.com/@userflow-tech/react-native/README.md), [troubleshooting.md](https://unpkg.com/@userflow-tech/react-native/docs/troubleshooting.md), [deep-linking.md](https://unpkg.com/@userflow-tech/react-native/docs/deep-linking.md), and [identity-verification.md](https://unpkg.com/@userflow-tech/react-native/docs/identity-verification.md). Do not quote warning strings from memory; search logs for the `[Userflow]` prefix.

---

## Step 1 — Analyze the project

Inspect before asking, and determine:

| Read | Determine |
|---|---|
| `AGENTS.md`, `CLAUDE.md`, `README` | Project rules, read before writing code. Rules about where SDK code lives and gates such as "ask before installing" override this skill's default placement and steps. |
| `package.json` | Expo SDK and React Native versions; `expo-router` or `@react-navigation/native`; whether `@userflow-tech/react-native` or `userflow.js` is already installed; `react-native-safe-area-context`; a `test` script (Jest); `react-native-view-shot` in `expo.install.exclude` (Step 2). If `userflow.js` is in this app, follow rule 8 and "If installation goes wrong, do not switch to the web SDK". The SDK requires React Native 0.76 or later (`react-native-view-shot` 5.x does not install below that). If this app is older, stop and say so. Do not upgrade React Native unless the developer explicitly agrees (rule 6). The SDK is tested up to Expo SDK 57. Expo SDK 58 and later bundle `react-native-webview` 14 and `react-native-view-shot` 6, which are outside the SDK's peer ranges. On Expo SDK 58 or later, tell the developer that version is not supported yet and stop. Do not force older WebView or view-shot versions onto it. |
| Lockfile and `.yarnrc.yml` | npm, Yarn 2+, or pnpm |
| `app.json` / `app.config.*`, `ios/`, `android/`, `babel.config.js` | Expo or bare; an existing Userflow config plugin; whether `babel.config.js` exists, its plugins, and `api.cache(true)` |
| Root layout or `App.tsx`, and the auth code | Where `init()`, `identify()`, `reset()`, and `UserflowProvider` belong; the user-id field; or that the app has no sign-in (Step 4) |
| An existing analytics, adoption, or tracking wrapper | Whether the app routes identity through its own layer. If it does, implement the SDK inside that wrapper instead of adding direct calls to the root layout, and say so in the confirmation. |
| Search the source for `userflow`, `Userflow`, and `identifyAnonymous(` | Existing Userflow code (rule 5). If the app already calls `identifyAnonymous()`, even through a no-op wrapper, ask whether to keep it before it reaches the real SDK: anonymous users count toward MAU (rule 1). |

Confirm once, naming the real stack — e.g. *"Expo SDK 57 with Expo Router; the current user comes from `useAuth()` in `src/auth/AuthProvider.tsx`; the id is `user.id`, the same id the web app already sends to Userflow. I'll init at startup, identify whenever a user is signed in, reset on sign-out, and add the Babel plugin so you can select elements on the device. Correct?"* — then continue. Ask whether that id matches the web install when the customer has one. Also ask whether the environment has identity verification enabled. If it does, `identify()` fails without a signature from the customer's backend, so the Advanced identity verification item is required.

No repository access: do not invent paths. Ask for the stack, auth entry points, and user-id field, or switch to the Developer Handoff Spec and stop.

## Step 2 — Install the packages

List every native module in the app's own `package.json`. Expo SDK 53 and older, and bare React Native, do not autolink packages that are only transitive dependencies. Leave out a package the app already lists at a version that satisfies the SDK, so its existing pin is kept.

On Expo SDK 56 and 57, check `expo.install.exclude` in `package.json` first. If it lists `react-native-view-shot` (left by the 0.4.4 README or by an app upgraded from SDK 55 or older), remove that entry before installing. With it in place, Expo installs the latest view-shot instead of 5.1.0, and `npx expo-doctor` skips the check, so nothing flags it.

```bash
# Expo SDK 56–57 (drop any package the app already lists at a satisfying version)
npx expo install @userflow-tech/react-native @react-native-async-storage/async-storage react-native-view-shot react-native-webview

# Expo SDK 55 and older (same rule; pin view-shot, see below)
npx expo install @userflow-tech/react-native @react-native-async-storage/async-storage react-native-view-shot@^5.0.0 react-native-webview

# Bare React Native (same rule)
npm install @userflow-tech/react-native '@react-native-async-storage/async-storage@^2' 'react-native-device-info@<16' 'react-native-view-shot@^5.0.0' 'react-native-webview@>=13.8.0 <14'
cd ios && pod install
```

Keep the version ranges in the bare command. Unpinned, npm picks the latest majors: `react-native-webview` 14 is outside the SDK's range, and npm only warns `ERESOLVE overriding peer dependency` and installs it anyway. AsyncStorage 3 sits next to the SDK's own 2.x copy, which leaves two copies of one native module. Treat an `overriding peer dependency` warning as a failed install. `npx expo install` picks Expo's bundled versions, which fit the SDK's ranges on Expo SDK 53–57, except view-shot on Expo SDK 55 and older.

Use the app's package manager. On Expo SDK 56 and 57, leave view-shot unpinned. Expo bundles 5.1.0, which satisfies `^5.0.0`. A `^5.0.0` pin resolves the newest 5.x on a fresh install, and `npx expo-doctor` then fails ("expected 5.1.0, found 5.1.1"). If that happened, rerun `npx expo install react-native-view-shot` instead of adding an exclude, after removing any view-shot exclude (above). With the exclude still set, the rerun keeps 5.1.1, and installing view-shot on its own can pull 6.x (outside `^5.0.0`).

On Expo SDK 55 and older, unpinned `npx expo install react-native-view-shot` resolves 4.0.3, which does not satisfy `^5.0.0`. If `package.json` already has view-shot below 5, keep `react-native-view-shot@^5.0.0` in the same install command as `@userflow-tech/react-native`. Installing the SDK alone fails with `ERESOLVE`. The two lines that matter are `Found: react-native-view-shot@4.0.3` and `peer react-native-view-shot@"^5.0.0" from @userflow-tech/react-native`. Rerun the Expo SDK 55 and older command above. Do not retry with `--force` or `--legacy-peer-deps`; that installs the SDK and leaves 4.0.3 in place. On Expo SDK 55 and older, in the same step as pinning `^5.0.0`, add `"react-native-view-shot"` to `expo.install.exclude` in `package.json` (`"expo": { "install": { "exclude": ["react-native-view-shot"] } }`). Without it, `npx expo-doctor` fails ("expected 4.0.3, found 5.1.1") and `npx expo install --fix` downgrades view-shot to 4.0.3. That downgrade reports success, with only an `overriding peer dependency` warning, and `npx expo-doctor` then passes, so check `npm ls react-native-view-shot` too. Once the exclude is set, always install view-shot as `react-native-view-shot@^5.0.0`. Unpinned, Expo skips its version, so npm can keep 4.0.3 or pull 6.x.

`react-native-device-info` is for bare React Native. Expo reads the app version from `expo-constants`.

Install `react-native-safe-area-context` unless the app already depends on it. Without it, banners, flow cards, and Builder bars draw under the status bar and home indicator. Expo Router and React Navigation apps usually have it already; a `SafeAreaProvider` in the tree is not a substitute for the package. Ask the developer whether to add the optional peers: `@react-native-community/netinfo` reconnects instantly when the network returns, and `expo-secure-store` keeps Builder pairing across an app restart (without it, they re-scan the QR code after every restart). On Expo, recommend both: `npx expo install @react-native-community/netinfo expo-secure-store` picks versions that match the SDK, and the app needs a native rebuild anyway. In bare React Native, pin these too: `'react-native-safe-area-context@<6'` and `'@react-native-community/netinfo@<13'`. Recommend NetInfo there, and `expo-secure-store` only when the app already has Expo modules (it needs them).

## Step 3 — Register the deep-link scheme

Ask for the environment's `scheme_id`. It starts with `userflow-` (for example `userflow-xxxxxxxxxxxxxxxxxxxxxxxxxx`). Reject an environment UUID and the app's own scheme.

Expo, in `app.json` or `app.config.js`:

```json
["@userflow-tech/react-native", { "schemeId": "<scheme_id>" }]
```

`npx expo install` already added a bare `"@userflow-tech/react-native"` entry to `plugins`. Once you have the `scheme_id`, replace that entry with the one above. Never leave both, and never leave the bare one once a `scheme_id` is known.

No `scheme_id` yet: keep the bare entry. The plugin then changes nothing, and prebuild prints `No schemeId was passed…`. Tell the developer that pairing and preview links won't open the app until it is set, and record the `scheme_id` as pending in AGENTS.md (Step 10).

Bare React Native: follow `docs/deep-linking.md` inside the installed package ([public copy](https://unpkg.com/@userflow-tech/react-native/docs/deep-linking.md)) for the `Info.plist` and `AndroidManifest.xml` entries.

## Step 4 — init, identify, reset

```tsx
import { Userflow } from '@userflow-tech/react-native';

await Userflow.init({ clientToken }); // once per process; safe to call again with the same options
await Userflow.identify(user.id, { name: user.name, email: user.email });
```

- `init` at startup, before `identify`. A second `init` with different options is ignored until the app restarts. When startup code and the auth code both need it, put the `init` call in one small module that both await.- `identify` wherever the app learns who the current user is: an auth-state listener or the current-user value from the auth context. Hooking only the sign-in function misses sign-up, demo or magic-link sign-in, and restored sessions. Await `init` first.
- `reset` when a signed-in user signs out.
- No sign-in at all: there is no user to identify, and flows and Builder previews only reach an identified user (a preview link waits for `identify`). Tell the developer. The only option is `identifyAnonymous()`, which counts every device that opens the app toward MAU (rule 1). Add it only with an explicit yes. Add no `reset()`, since nothing signs out. If they decline, finish the rest of the install and tell them that flows and the Step 9 preview check won't work until the app identifies a user.
- Read `clientToken` from the app's env config. One token per environment. A value that does not start with `ct_` is a placeholder: skip `init` for that environment and tell the developer. Never replace it with a guess.
- No env config yet: on Expo, add `EXPO_PUBLIC_USERFLOW_CLIENT_TOKEN=<the ct_ token>` to `.env` at the project root. Edit the file if it exists; never overwrite it (for example with `echo … > .env`). Read it as `process.env.EXPO_PUBLIC_USERFLOW_CLIENT_TOKEN`; Expo inlines only that dot-notation form. Fully reload the app after changing `.env`. If `.env` is gitignored, EAS Build doesn't receive it, so tell the developer to set the same variable in EAS too. The `ct_` token ships in the app and isn't a secret. Bare React Native has no built-in env loader: ask how the app handles config before adding a package for it.
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

  If `app/+native-intent.ts` already exists, wrap it instead of overwriting it. `createRedirectSystemPath({ next })` does not call `next` for Userflow links, so host logic that must see every URL (logging, analytics) runs first, and the host's remaining redirect logic goes in `next`:

  ```ts
  import { createRedirectSystemPath, type RedirectSystemPathOptions } from '@userflow-tech/react-native/expo-router';

  const userflowRedirect = createRedirectSystemPath({ next: hostRedirect }); // omit `next` if the host only logs
  export function redirectSystemPath(event: RedirectSystemPathOptions) {
    try {
      hostLog(event);
    } catch {
      // Expo warns that throwing here can crash the app on launch.
    }
    return userflowRedirect(event);
  }
  ```
- **React Navigation:** wrap the navigator with `WithUserflowReactNavigation`.
- **Anything else:** call `Userflow.updateScreen(name)` (or `useUserflowScreen`) when the screen changes.

## Step 7 — Babel plugin (on-device element selection)

Always add `@userflow-tech/react-native/babel-plugin`. It stamps `View`, `Text`, `Pressable`, the Touchables, `TextInput`, and `Image` at build time, so authors can select elements on the paired device in the Builder and target them without a `testID`. Without it, on-device selection only finds elements that already have an id, a label, or a press handler, and codeless selectors lose their scored match when a flow plays. Keep the default full mode; `stampOnly: true` leaves the picker's registry empty.

1. No `babel.config.js` (common on Expo): create it with `npx expo customize babel.config.js`. Bare React Native already has one.
2. Add the plugin to `plugins`, keeping the app's presets and plugins. If `plugins` lists `react-native-reanimated/plugin` or `react-native-worklets/plugin`, keep that one last.
3. If the app has Jest, skip this plugin under test: Jest reads the same config, and the stamps rewrite snapshots. Keep the app's own plugins in every environment, including under test. Remove `api.cache(true)`, because calling it before `api.env` throws `Caching has already been configured`, and `api.env` already caches per environment:

   ```js
   module.exports = function (api) {
     const isTest = api.env('test');
     return {
       presets: ['babel-preset-expo'], // keep the app's own presets
       plugins: [
         // ...the app's own plugins
         ...(isTest ? [] : ['@userflow-tech/react-native/babel-plugin']),
         // react-native-reanimated/plugin or react-native-worklets/plugin, if present, stays last
       ],
     };
   };
   ```

Tell the developer that stamped ids come from the file path, sibling order, and static labels, so moving a file or reordering elements can break a codeless selector. For elements a key flow depends on, a `testID` is still the most durable target.

## Step 8 — Jest

If the app has Jest, mock the SDK in the Jest setup file so tests do not load native modules. Copy the mock from the Jest section of the installed package README. Include the methods the app calls, and also mock the router entry the app imports (`@userflow-tech/react-native/expo-router` or `/navigation`), with every export the app uses from it. In a TypeScript setup file, type the provider's `children` as `ReactNode` so strict mode passes.

Expo Router loads `app/+native-intent.ts` when a test renders the router, so the `/expo-router` mock also needs what that file imports. Use these stubs; a bare `jest.fn()` returns `undefined` and breaks the router or the wrapper:

```ts
jest.mock('@userflow-tech/react-native/expo-router', () => ({
  UserflowExpoRouterScreenTracker: () => null,
  redirectSystemPath: ({ path }: { path: string }) => path,
  createRedirectSystemPath:
    ({ next }: { next?: (event: { path: string }) => unknown } = {}) =>
    (event: { path: string }) =>
      next ? next(event) : event.path,
}));
```

## Step 9 — Verify

You run:

- The app's typecheck.
- The app's tests, if it has them.
- `npx expo-doctor` (Expo).
- `npm ls react-native-view-shot` (or the package manager's equivalent) shows no `invalid` line. A passing `npx expo-doctor` does not prove it: an exclude hides the check, and `--fix` can leave 4.0.3.
- The Babel plugin stamps: `node -e 'console.log(/nativeID: ?"uf_/.test(require("@babel/core").transformFileSync(process.argv[1]).code))' <file>` prints `true`. Pick a file whose code literally uses the tag `<View>` or `<Text>` on an element without a `testID`, `nativeID`, or `userflowId`. The plugin matches the tag name, not the import, so a file that renders an aliased import such as `<DefaultView>`, or only wrappers such as `<ThemedView>`, prints `false` even when the plugin works.
- A bundle: `npx expo export --platform ios`, or `react-native bundle` for bare React Native. Delete the output afterwards (`expo export` writes `dist/`).

If the typecheck reports errors from inside `node_modules/@userflow-tech/react-native/src` (a missing `.png` module or `@react-navigation/native`), the installed SDK version is too old for Expo's TypeScript setup. Tell the developer and suggest a newer version. Do not add stub declarations or extra dependencies to the app without their OK.

Then hand the customer the steps you cannot do:

1. Rebuild and launch the native app. A Metro reload is not enough. With Expo, if `ios/` or `android/` already exists, `npx expo run:*` does not re-run prebuild, so the new scheme and native modules never reach the native project. Run `npx expo prebuild` first (never `--clean` without a yes). If those folders are committed and hand-edited, treat the app as bare and check the scheme in `Info.plist` and `AndroidManifest.xml`. Start Metro with a cleared cache once (`npx expo start -c`, or `npx react-native start --reset-cache`) so every file is stamped.
2. Confirm the dev console has no `[Userflow]` setup warning. A complete install stays quiet. The SDK runs these checks inside `Userflow.init`, so with a placeholder token (init skipped) a quiet console proves nothing. Repeat this check once a real `ct_` token is set.
3. In the Builder, open Preview → "Pair a device" and scan the QR code. The app shows a "Preview mode" bar. Then press Preview.
4. Select a tooltip target on the device, choosing an element without a `testID`. If it can't be selected, check that the Babel plugin is in the config and that Metro was started with a cleared cache.

Search device logs for `[Userflow]` if any of those fail, and match the line to `docs/troubleshooting.md` ([public copy](https://unpkg.com/@userflow-tech/react-native/docs/troubleshooting.md)).

## If installation goes wrong, do not switch to the web SDK

`@userflow-tech/react-native` is the SDK for this app. Do not install `userflow.js`, and do not follow the Userflow.js pages on help.userflow.com, because a step failed (rule 8).

- The install and API pages on help.userflow.com describe Userflow.js. Do not apply their code here.
- The server error `Invalid Userflow.js Token` is the backend's name for the client token. It means the `ct_` token is wrong, not that `userflow.js` is needed.
- `window is not defined` or `document is not defined` means web code got into the native bundle. Remove that code; do not add more of it.
- `userflow.js` already present in this app's `package.json` or imports is a leftover from a wrong-SDK attempt. Report it and remove it only with a yes. In a monorepo, leave a separate web app's `userflow.js` alone.
- This SDK supports iOS and Android only.

## Step 10 — Document

Add or update the "Userflow installation" section in `AGENTS.md` (or `CLAUDE.md`), as described at the top. Never overwrite the rest of the file. If existing notes say something the install made false (for example "SDK not installed yet"), list those lines and propose edits; don't only append.

---

## Developer Handoff Spec

Without repository access, do not write code. Generate `USERFLOW_RN_INSTALL_SPEC.md` containing: how to detect Expo vs bare and the router; the install commands; where `scheme_id` and `clientToken` come from; the `init` / `identify` / `reset` / provider / screen-tracking code with the customer's real user-id field named; the Babel plugin config; the Jest mock note; the core rules; and the Step 9 checklist. The document must stand on its own.

## Advanced — only when the customer asks

- **`identifyAnonymous()`.** Opt-in identification of signed-out users. They count toward MAU. Not a fallback for `identify()`. Requires the customer's explicit consent, and requires AsyncStorage to be linked.
- **Identity verification.** Required when the environment has it enabled (Step 1); otherwise ask first. The signature is an HMAC-SHA256 of the user id, computed on the customer's backend with the identity verification secret key (`esk_...`), and passed as `identify(id, attrs, { signature })`. Follow the installed `docs/identity-verification.md` ([public copy](https://unpkg.com/@userflow-tech/react-native/docs/identity-verification.md)). The secret never ships in the app.
- **`group()` and `track()`.** `group()` after `identify()`, with a real group id. `track()` only once a user is identified.

## Reference

- Installed `node_modules/@userflow-tech/react-native/README.md` — install, placement, API, Jest. [Public copy](https://unpkg.com/@userflow-tech/react-native/README.md).
- Installed `docs/troubleshooting.md` — [public copy](https://unpkg.com/@userflow-tech/react-native/docs/troubleshooting.md).
- Installed `docs/deep-linking.md` — [public copy](https://unpkg.com/@userflow-tech/react-native/docs/deep-linking.md).
- Installed `docs/identity-verification.md` — [public copy](https://unpkg.com/@userflow-tech/react-native/docs/identity-verification.md).
- [Identity verification](https://help.userflow.com/docs/identity-verification) — the concept only. The code for this SDK is in `docs/identity-verification.md`.
