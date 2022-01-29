export default function logAppLaunch() {
    fetch("/analytics/launch", { method: "POST" });
}
