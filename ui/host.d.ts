// Host-owned globals emitted by Flaxon routing and the configured PWA plugin.
interface Window {
  __TELOCE_ROUTER__: { navigate(path: string): unknown };
}
interface CoursePwaController {
  updateAvailable: boolean;
  activateUpdate(): unknown;
}
declare var telocePlugins: {
  pwa?: CoursePwaController | Promise<CoursePwaController | undefined>;
} | undefined;
