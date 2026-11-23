"""关键业务的规则覆盖与优先级回归；Geo 数据库由 Mihomo 单独验证。"""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("check_rules", Path(__file__).resolve().parents[1] / "scripts/check-rules.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class RoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules, _ = checker.load_rules()

    def test_domain_routes(self):
        cases = {
            "🤖 AI 服务": ["chatgpt.com", "ws.chatgpt.com", "cdn.openaimerge.com", "openaiassets.blob.core.windows.net",
                        "images.workoscdn.com", "chatgpt.livekit.cloud", "crixet.com", "claudeacademy.com", "api.anthropic.com", "platform.claude.com",
                        "random.claudemcpcontent.com", "random.claudemcpclient.com", "a.claudeusercontent.com", "studio.claudestudio.com",
                        "docs.anthropic.team", "api.ant.dev", "auth.anthropic.auth0.com",
                        "fcmtoken.googleapis.com", "r.stripe.com", "us.sentry.io", "cdn.anthropic.com.cdn.cloudflare.net",
                        "js.hcaptcha.com", "verify.withpersona.com", "api.yoti.com", "support.intercom.io",
                        "assets.intercomassets.com", "api.siftscience.com",
                        "downloads.cursor-cdn.com", "a.b.cursorvm.com", "api.cursorapi.com",
                        "copilot-proxy.githubusercontent.com", "api.individual.githubcopilot.com",
                        "production-copilot-host.webpubsub.azure.com", "api.codeiumdata.com", "api.devin.ai",
                        "accounts.spacex.ai", "grazie.aws.intellij.net", "cas-bridge.xethub.hf.co", "demo.hf.space",
                        "pplx.ai", "api.elevenlabs.io", "challenges.cloudflare.com"],
            "🎵 TikTok": ["open.tiktokapis.com", "open-api.tiktokglobalshop.com", "v16.tiktokcdn-us.com",
                        "a.tiktokcdn-eu.com", "p16.tiktokcdn.com.akamaized.net", "pippit.ai", "api.capcutapi.us"],
            "🔍 Google": ["redirector.xn--ngstr-lra8j.com", "r1---sn-test.xn--ngstr-lra8j.com",
                         "services.googleapis.cn", "play-fe.googleapis.com", "gemini.google.com", "ai.studio",
                         "deepmind.google", "antigravity-unleash.goog", "us-docker.pkg.dev"],
            "🇺🇳 国外网站": ["github.com", "release-assets.githubusercontent.com", "ghcr.io", "demo.github.dev",
                            "productionresultssa180.blob.core.windows.net", "npmregistryv2prod.blob.core.windows.net",
                            "marketplace.visualstudio.com", "vscode.download.prss.microsoft.com",
                            "playwright.download.prss.microsoft.com", "a.gallerycdn.vsassets.io", "open-vsx.org",
                            "cdn.jsdelivr.net", "static.crates.io", "download.jetbrains.com", "dropbox.com", "netflix.com",
                            "shopify.dev", "www.futuhk.com", "api.moomoo.com", "sg.itiger.com",
                            "a.tigerbrokers.net", "longbridge.com", "origin.longbridge.com", "longbridge.sg",
                            "api.longbridge-inc.com", "mnt-report.skytigris.cn", "c1.itigergrowtha.com",
                            "www.tigrwd.com"],
            "🏠 家宽节点": ["admin.shopify.com", "accounts.shopify.com", "cdn.shopify.com", "demo.myshopify.com",
                         "extensions.shopifycdn.com", "shop.app", "shop.com", "js.stripe.com", "stripecdn.com", "stripe.network"],
            "Ⓜ️ 微软服务": ["office.com", "login.microsoftonline.com", "www.microsoft.com"],
            "🔵 Meta 服务": ["facebook.com", "instagram.com", "meta.ai"],
            "🐟 规则之外": ["notgoogle.example", "google.com.example", "xn--ngstr-lra8z.com", "claude.code", "xai.com",
                         "notmyshopify.com", "admin.shopify.com.example"],
        }
        for policy, domains in cases.items():
            for domain in domains:
                with self.subTest(domain=domain):
                    self.assertEqual(checker.match_local(self.rules, domain=domain), policy)

        for domain in ["futu.com.example", "notmoomoo.com", "tigerbrokers.com.example", "longbridge.com.example"]:
            with self.subTest(domain=domain):
                self.assertEqual(checker.match_local(self.rules, domain=domain), "🐟 规则之外")

    def test_ip_ranges(self):
        for ip in ["119.28.37.77", "43.153.233.212", "124.156.233.21", "170.106.49.68",
                   "119.91.245.125", "43.153.191.154", "101.32.198.91"]:
            with self.subTest(ip=ip):
                self.assertEqual(checker.match_local(self.rules, ip=ip), "🇺🇳 国外网站")
        for ip in ["160.79.104.1", "153.61.227.254", "2607:6bc0::1", "209.249.57.1"]:
            with self.subTest(ip=ip):
                self.assertEqual(checker.match_local(self.rules, ip=ip), "🤖 AI 服务")
        self.assertEqual(checker.match_local(self.rules, ip="2607:6bc0:1::1"), "🐟 规则之外")
        # 私网优先，不因域名是 AI 服务就把局域网地址发送到境外。
        self.assertEqual(checker.match_local(self.rules, domain="api.openai.com", ip="192.168.1.1"), "DIRECT")
        for ip in ["::1", "fc00::1", "fe80::1"]:
            with self.subTest(ip=ip):
                self.assertEqual(checker.match_local(self.rules, ip=ip), "DIRECT")

    def test_no_unsupported_tiktok_geoip(self):
        self.assertNotIn(["GEOIP", "tiktok", "no-resolve"], [parts for parts, _, _ in self.rules])
        self.assertIn(["GEOSITE", "tiktok"], [parts for parts, _, _ in self.rules])


if __name__ == "__main__":
    unittest.main()
