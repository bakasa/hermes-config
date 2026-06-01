# South Africa Market — Default Tech Choices

When building for the South African market, use these defaults unless the user specifies otherwise.

## SMS
**Provider:** WinSMS (`winsms.co.za`)
- API: HTTP GET (simplest), REST, or SOAP
- Endpoint: `https://www.winsms.co.za/api/batchmessage.asp`
- Auth: Username + Password (no API key)
- Cost: ~R0.24/SMS, pay-per-credit, no monthly fees
- Sender ID: Register a custom one (11 chars max, no spaces)
- Phone format: Convert `+27xxxxxxxxx` → `0xxxxxxxxx`
- Response: `"OK: MessageID=12345"` or `"ERROR: Description"`
- Two-way: Replies route to email or WinSMS inbox
- Integration: Plain `HttpClient`, no vendor SDK needed

```csharp
public class WinSmsService(IConfiguration config)
{
    private readonly string _username = config["WinSMS:Username"]!;
    private readonly string _password = config["WinSMS:Password"]!;
    private readonly string _senderId = "YourBrand";
    private readonly HttpClient _http = new();

    public async Task<string> SendSms(string toZaPhone, string message)
    {
        var local = toZaPhone.StartsWith("+27") ? "0" + toZaPhone[3..] : toZaPhone;
        var url = $"https://www.winsms.co.za/api/batchmessage.asp" +
                  $"?User={_username}&Pass={_password}" +
                  $"&Numbers={Uri.EscapeDataString(local)}" +
                  $"&Message={Uri.EscapeDataString(message)}" +
                  $"&From={_senderId}";
        return await _http.GetStringAsync(url);
    }
}
```

## Payments
**Primary:** Paystack (paystack.com) — SA champion, .NET SDK available
- Cards, EFT, mobile money, QR codes
- Webhook-driven async confirmation
- 1.5% + R10 per transaction
- `PAYSTACK_SECRET_KEY` + `PAYSTACK_PUBLIC_KEY`

**Secondary:** SnapScan (snapscan.co.za) — QR-based, popular in SA

**Always support cash** — ~60% of SA adults are underbanked. Record cash payments in-app with driver confirmation.

## Maps
**Provider:** Mapbox (mapbox.com)
- SA coverage is excellent
- Free tier: 50k loads/month
- Directions API + Geocoding + Static Maps

## Push Notifications
**Provider:** Firebase Cloud Messaging (FCM)
- Free tier is generous
- Works on iOS + Android + Web
- Pair with Firebase Auth for mobile OTP

## Auth
**Mobile:** Firebase Auth (phone OTP)
**Web/Backend:** ASP.NET Identity + JWT
- JWT_ISSUER / JWT_AUDIENCE = your brand name (lowercase)
- OTP via WinSMS SMS

## Database
**PostgreSQL + PostGIS** — geo-queries for nearby-driver searches (ST_DWithin)
**Redis** — session store, rate limiting, SignalR backplane

## Hosting
**Railway** (railway.app) — managed PG + Redis + Docker deploys
- Use Dockerfile per service
- Railway auto-provisions `PGHOST`, `PGUSER`, `PGPASSWORD`

## SA Market Non-Negotiables
1. **Cash payments** — must-have, not optional
2. **Offline-first** — load shedding (power outages) is frequent
3. **Multi-language** — at minimum: English, isiZulu, Afrikaans
4. **Safety features** — SOS button, share ride, driver vetting (non-negotiable for SA)
5. **Low data usage** — app <10MB, aggressive caching, bandwidth-efficient
6. **Android 8+** — wide device diversity, many low-end phones
7. **WinSMS for SMS** — cheaper, SA-native, simpler than Twilio
