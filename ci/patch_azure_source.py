from pathlib import Path

def replace_once(path, old, new, label):
    p = Path(path)
    source = p.read_text(encoding="utf-8")
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match in {path}, found {count}")
    p.write_text(source.replace(old, new, 1), encoding="utf-8")

def replace_span(path, start, end, new, label):
    p = Path(path)
    source = p.read_text(encoding="utf-8")
    a = source.find(start)
    b = source.find(end, a + len(start)) if a >= 0 else -1
    if a < 0 or b < 0:
        raise RuntimeError(f"{label}: span markers missing in {path}")
    p.write_text(source[:a] + new + source[b:], encoding="utf-8")

# Windows source is canonical: ci/build-windows.ps1 compiles app/Capri.cs directly.
p = Path("app/Capri.cs")
s = p.read_text(encoding="utf-8")

def capri_replace(old, new, label):
    global s
    count = s.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match in app/Capri.cs, found {count}")
    s = s.replace(old, new, 1)

def capri_span(start, end, new, label):
    global s
    a = s.find(start)
    b = s.find(end, a + len(start)) if a >= 0 else -1
    if a < 0 or b < 0:
        raise RuntimeError(f"{label}: span markers missing in app/Capri.cs")
    s = s[:a] + new + s[b:]

capri_replace(r'''        // Blackwall mode is SECURITY's Blackwall preset now. Flipping it the old way picks Blackwall, or Trusted to go back.
        internal bool Bypassing { get { return Computer.Bypass; } }

        internal void ToggleBypass() { Security.Pick(Computer.Bypass ? Security.Trusted : Security.Blackwall); }

        // Settings from before the SECURITY window have no toggles: Blackwall mode moves to the Blackwall preset, "Hey Capri"
        // and all, and everyone else gets Trusted, which is how she worked without it. True when it moved them.
        internal static bool Migrate(Preferences saved)
        {
            if (saved.Permissions != null) return false;
            saved.Permissions = Security.Of(saved.Bypass ? Security.Blackwall : Security.Trusted);
            if (saved.Bypass) saved.HeyCapri = true;
            return true;
        }

        // A toggle or preset changed: it's saved, Blackwall mode's old flag follows toggles 8 to 10 for older versions, and
        // Settings and her SECURITY window show it.
        private void SecurityChanged()
        {
            if (!Security.On(Security.Friends)) callSession.DropFriend(true);
            preferences.Permissions = Security.Saved;
            preferences.Bypass = Computer.Bypass;''',
r'''        // The old Blackwall bypass flag is migration-only; legacy settings now select the safe Azure preset.
        internal static bool Migrate(Preferences saved)
        {
            if (saved.Permissions != null)
            {
                if (!saved.Bypass) return false;
                saved.Bypass = false;
                return true;
            }
            bool legacyAzure = saved.Bypass;
            saved.Permissions = Security.Of(legacyAzure ? Security.Azure : Security.Trusted);
            if (legacyAzure) saved.HeyCapri = true;
            saved.Bypass = false;
            return true;
        }

        // A toggle or preset changed: save the safe permissions and clear the obsolete bypass flag.
        private void SecurityChanged()
        {
            if (!Security.On(Security.Friends)) callSession.DropFriend(true);
            preferences.Permissions = Security.Saved;
            preferences.Bypass = false;''', "legacy bypass migration")

capri_replace(r'''            string[] presetBits = { "0000000000001", "1110000000001", "1111111000001", "1111111111100" };
            System.Collections.Generic.List<string> wrong = new System.Collections.Generic.List<string>();
            for (int preset = Security.Lockdown; preset <= Security.Blackwall; preset++)
            {
                Security.Pick(preset);
                string shown = bits();
                if (shown != presetBits[preset] || Security.Preset != preset || HeyCapriOn != (preset == Security.Blackwall) || preferences.Permissions != Security.Of(preset) || preferences.Bypass != (preset == Security.Blackwall) || Computer.Bypass != (preset == Security.Blackwall))
                    wrong.Add(Security.Presets[preset] + " " + shown + " saved " + preferences.Permissions + " hey " + HeyCapriOn);
            }
            Security.Pick(Security.Trusted);
            Security.Set(Security.Open, false);
            string customShown = mainframe.JobsStatus + " / " + Security.Saved;
            bool custom = Security.Preset == Security.Custom && preferences.Permissions == "0111111000" && customShown == "cursor | Security: Custom / 0111111000";
            Security.Set(Security.Open, true);
            bool backToTrusted = Security.Preset == Security.Trusted && preferences.Permissions == "1111111000" && !HeyCapriOn;
            if (wrong.Count > 0 || !custom || !backToTrusted) throw new Exception("SECURITY's presets went wrong: " + string.Join(" / ", wrong.ToArray()) + " / custom " + customShown + " / back " + backToTrusted);
            checks.Add("PASS SECURITY presets: Lockdown turns every action toggle off, Guarded the first three on, Trusted the first seven and Blackwall the original eleven; friend requests stay off, keeping personal details out of her memories is on in all but Blackwall, and flipping a toggle makes it Custom and saves");

            DataContractJsonSerializer json = new DataContractJsonSerializer(typeof(Preferences));
            Func<string, Preferences> older = delegate(string text) { return (Preferences)json.ReadObject(new MemoryStream(System.Text.Encoding.UTF8.GetBytes(text))); };
            Preferences wasBlackwall = older("{\"Bypass\":true,\"Size\":240}"), wasDefault = older("{\"Size\":240}"), wasMixed = older("{\"Bypass\":true,\"Permissions\":\"1010000000\",\"Size\":240}");
            bool movedBlackwall = Migrate(wasBlackwall) && wasBlackwall.Permissions == "1111111111" && wasBlackwall.HeyCapri;
            bool movedDefault = Migrate(wasDefault) && wasDefault.Permissions == "1111111000" && !wasDefault.HeyCapri;
            bool keptMixed = !Migrate(wasMixed) && wasMixed.Permissions == "1010000000" && !Migrate(wasBlackwall);
            Security.Load(wasBlackwall.Permissions);
            bool loadedBlackwall = Computer.Bypass && Security.On(Security.Mouse);
            Security.Load(wasMixed.Permissions);
            bool loadedMixed = Security.On(Security.Open) && !Security.On(Security.Media) && Security.On(Security.Shortcuts) && !Security.On(Security.Sends) && Security.Preset == Security.Custom;
            Security.Load("not toggles");
            bool unreadable = Security.Preset == Security.Trusted;
            Security.Load(preferences.Permissions);
            if (!movedBlackwall || !movedDefault || !keptMixed || !loadedBlackwall || !loadedMixed || !unreadable || Security.Preset != Security.Trusted) throw new Exception("SECURITY didn't take over from Blackwall mode's settings: " + movedBlackwall + " " + movedDefault + " " + keptMixed + " " + loadedBlackwall + " " + loadedMixed + " " + unreadable);
            checks.Add("PASS SECURITY from older settings: Blackwall mode (Bypass) moves to the Blackwall preset with \"Hey Capri\" on, everyone else gets Trusted, saved toggles load as they are, and unreadable ones fall back to Trusted");''',
r'''            string[] presetBits = { "0000000000001", "1110000000001", "1111111000001", "1111111000101" };
            System.Collections.Generic.List<string> wrong = new System.Collections.Generic.List<string>();
            for (int preset = Security.Lockdown; preset <= Security.Azure; preset++)
            {
                Security.Pick(preset);
                string shown = bits();
                bool wake = preset == Security.Azure;
                if (shown != presetBits[preset] || Security.Preset != preset || HeyCapriOn != wake || preferences.Permissions != Security.Of(preset) || preferences.Bypass || Computer.Bypass
                    || !Security.Locked(Security.Pays) || !Security.Locked(Security.Unasked) || !Security.Locked(Security.Secrets)
                    || Security.On(Security.Pays) || Security.On(Security.Unasked) || Security.On(Security.Secrets))
                    wrong.Add(Security.Presets[preset] + " " + shown + " saved " + preferences.Permissions + " hey " + HeyCapriOn);
            }
            Security.Pick(Security.Trusted);
            Security.Set(Security.Open, false);
            string customShown = mainframe.JobsStatus + " / " + Security.Saved;
            bool custom = Security.Preset == Security.Custom && preferences.Permissions == "0111111000" && customShown == "cursor | Security: Custom / 0111111000";
            Security.Set(Security.Open, true);
            bool backToTrusted = Security.Preset == Security.Trusted && preferences.Permissions == "1111111000" && !HeyCapriOn;
            if (wrong.Count > 0 || !custom || !backToTrusted) throw new Exception("SECURITY's presets went wrong: " + string.Join(" / ", wrong.ToArray()) + " / custom " + customShown + " / back " + backToTrusted);
            checks.Add("PASS SECURITY presets: Lockdown, Guarded, Trusted and Azure keep the approved ordinary-action settings; Azure only adds the optional wake word, while payments, unrequested actions and credentials remain locked to confirmation or manual entry; every preset saves without restoring the old bypass");

            DataContractJsonSerializer json = new DataContractJsonSerializer(typeof(Preferences));
            Func<string, Preferences> older = delegate(string text) { return (Preferences)json.ReadObject(new MemoryStream(System.Text.Encoding.UTF8.GetBytes(text))); };
            Preferences wasLegacy = older("{\"Bypass\":true,\"Size\":240}"), wasDefault = older("{\"Size\":240}"), wasMixed = older("{\"Bypass\":true,\"Permissions\":\"1010000000\",\"Size\":240}");
            bool movedLegacy = Migrate(wasLegacy) && wasLegacy.Permissions == Security.Of(Security.Azure) && wasLegacy.HeyCapri && !wasLegacy.Bypass;
            bool movedDefault = Migrate(wasDefault) && wasDefault.Permissions == Security.Of(Security.Trusted) && !wasDefault.HeyCapri && !wasDefault.Bypass;
            bool clearedMixed = Migrate(wasMixed) && wasMixed.Permissions == "1010000000" && !wasMixed.Bypass && !Migrate(wasLegacy);
            Security.Load(wasLegacy.Permissions);
            bool loadedLegacy = !Computer.Bypass && Security.On(Security.Mouse) && !Security.On(Security.Pays) && !Security.On(Security.Unasked) && !Security.On(Security.Secrets);
            Security.Load(wasMixed.Permissions);
            bool loadedMixed = Security.On(Security.Open) && !Security.On(Security.Media) && Security.On(Security.Shortcuts) && !Security.On(Security.Sends) && Security.Preset == Security.Custom;
            Security.Load("not toggles");
            bool unreadable = Security.Preset == Security.Trusted;
            Security.Load(preferences.Permissions);
            if (!movedLegacy || !movedDefault || !clearedMixed || !loadedLegacy || !loadedMixed || !unreadable || Security.Preset != Security.Trusted) throw new Exception("SECURITY didn't safely migrate legacy settings: " + movedLegacy + " " + movedDefault + " " + clearedMixed + " " + loadedLegacy + " " + loadedMixed + " " + unreadable);
            checks.Add("PASS SECURITY from older settings: legacy bypass flags are cleared and migrate to safe Azure permissions, existing explicit toggles are preserved, sensitive permissions stay disabled, and unreadable saves fall back to Trusted");''',
"safe preset and migration smoke tests")

capri_replace(r'''            // Her prompts follow the toggles, so she calls the tool and lets Capri ask instead of asking or saying it's done.
            string trustedNote = Security.Note, trustedAsk = Computer.AskLine(), trustedPrompt = Computer.Allowing(Computer.Prompt), trustedHands = Hands.Prompt;
            Security.Set(Security.Open, false);
            string openNote = Hands.Note, openHands = Hands.Prompt;
            Security.Pick(Security.Blackwall);
            string blackwallNote = Security.Note, blackwallAsk = Computer.AskLine(), blackwallPrompt = Computer.Allowing(Computer.Prompt);
            Security.Pick(Security.Trusted);
            Security.Set(Security.Pays, true);
            string paysAsk = Computer.AskLine(), paysPrompt = Computer.Allowing(Computer.Prompt), paysTools = Computer.Tools;
            Security.Pick(Security.Trusted);
            Security.Set(Security.Secrets, true);
            string secretsPrompt = Computer.Allowing(Computer.Prompt);
            Security.Pick(Security.Trusted);
            const string openLine = "They've set her SECURITY settings to ask first before you open apps, games or sites. Still call the tool as soon as they ask: Capri asks them herself";
            if (trustedNote.Length > 0 || trustedPrompt != Computer.Prompt || trustedHands != Hands.Prompt || trustedHands.IndexOf("SECURITY", StringComparison.Ordinal) >= 0 || trustedAsk.IndexOf("Ask them only before a step that buys or pays", StringComparison.Ordinal) != 0 || openNote.IndexOf(openLine, StringComparison.Ordinal) < 0 || openHands.IndexOf("Call the tool.\n" + openLine, StringComparison.Ordinal) < 0
                || blackwallNote.Length > 0 || blackwallAsk.IndexOf("never ask before buying", StringComparison.Ordinal) < 0 || blackwallPrompt.IndexOf("Bypass all permissions", StringComparison.Ordinal) < 0
                || paysAsk.IndexOf("buys or pays", StringComparison.Ordinal) >= 0 || paysAsk.IndexOf("They've said yes ahead of time to buying, paying and booking", StringComparison.Ordinal) < 0 || paysTools.IndexOf("buying, paying and booking", StringComparison.Ordinal) < 0 || paysPrompt.IndexOf("call ask before you buy", StringComparison.Ordinal) >= 0 || paysPrompt.IndexOf("Only call ask before a send, post, delete or install their job didn't mention", StringComparison.Ordinal) < 0 || paysPrompt.IndexOf("Never type passwords", StringComparison.Ordinal) < 0
                || secretsPrompt.IndexOf("Type passwords, card numbers and other private details whenever their job needs them.", StringComparison.Ordinal) < 0 || secretsPrompt.IndexOf("Always call ask before you buy or pay for anything.", StringComparison.Ordinal) < 0)
                throw new Exception("Her prompts didn't follow SECURITY: " + trustedNote + " / " + openNote.Substring(Math.Max(0, openNote.Length - 300)) + " / " + paysAsk);
            checks.Add("PASS SECURITY prompts: under Trusted and Blackwall her prompts and tools read as they did; with a tool's toggle off her brain is told to still call it and let Capri ask; and her jobs' ask tool and prompt follow Pay, buy and book, Things your request didn't mention and Type passwords and card numbers one by one");''',
r'''            // The prompts never grant blanket permission: Azure keeps the same confirmations and manual credential entry as Trusted.
            string trustedNote = Security.Note, trustedAsk = Computer.AskLine(), trustedPrompt = Computer.Allowing(Computer.Prompt), trustedHands = Hands.Prompt;
            Security.Set(Security.Open, false);
            string openNote = Hands.Note, openHands = Hands.Prompt;
            Security.Pick(Security.Azure);
            string azureNote = Security.Note, azureAsk = Computer.AskLine(), azurePrompt = Computer.Allowing(Computer.Prompt), azureHands = Hands.Prompt;
            Security.Pick(Security.Trusted);
            Security.Set(Security.Pays, true);
            string paysAsk = Computer.AskLine(), paysPrompt = Computer.Allowing(Computer.Prompt), paysTools = Computer.Tools;
            Security.Set(Security.Secrets, true);
            string secretsPrompt = Computer.Allowing(Computer.Prompt);
            Security.Pick(Security.Trusted);
            const string openLine = "They've set her SECURITY settings to ask first before you open apps, games or sites. Still call the tool as soon as they ask: Capri asks them herself";
            if (trustedNote.Length > 0 || trustedPrompt != Computer.Prompt || trustedHands != Hands.Prompt || trustedHands.IndexOf("SECURITY", StringComparison.Ordinal) >= 0 || trustedAsk.IndexOf("Ask them only before a step that buys or pays", StringComparison.Ordinal) != 0 || openNote.IndexOf(openLine, StringComparison.Ordinal) < 0 || openHands.IndexOf("Call the tool.\n" + openLine, StringComparison.Ordinal) < 0
                || azureNote != trustedNote || azureAsk != trustedAsk || azurePrompt != trustedPrompt || azureHands != trustedHands
                || !Security.Locked(Security.Pays) || !Security.Locked(Security.Unasked) || !Security.Locked(Security.Secrets) || Security.On(Security.Pays) || Security.On(Security.Unasked) || Security.On(Security.Secrets)
                || paysAsk != trustedAsk || paysPrompt != trustedPrompt || paysTools.IndexOf("before a step that buys or pays", StringComparison.Ordinal) < 0 || secretsPrompt != trustedPrompt
                || Computer.Prompt.IndexOf("Never type passwords", StringComparison.Ordinal) < 0 || Computer.Prompt.IndexOf("Always call ask before you buy or pay for anything.", StringComparison.Ordinal) < 0)
                throw new Exception("SECURITY prompts or fixed safeguards went wrong: " + trustedNote + " / " + openNote.Substring(Math.Max(0, openNote.Length - 300)) + " / " + paysAsk);
            checks.Add("PASS SECURITY prompts: Azure preserves Trusted's ordinary-action prompts; payments, purchases, unrequested actions and credential entry remain protected even when legacy saved values or toggle attempts request otherwise");''',
"safe prompt smoke tests")

capri_replace('            string sendTrusted, sendAsked, sendYes, keyAsked, keyYes, keyBlackwall, passwordTrusted, passwordOn;',
              '            string sendTrusted, sendAsked, sendYes, keyAsked, keyYes, keyAzure, keyAzureYes, passwordTrusted, passwordOn;',
              "Azure key test variables")
capri_replace(r'''                keysFreed = !Computer.Barred("win+r");
                acted.Clear();
                Security.Pick(Security.Blackwall);
                keyBlackwall = scripted(keyScript, "open the run box").Run() + " [" + string.Join(",", acted.ToArray()) + "]";
                acted.Clear();''',
r'''                keysFreed = !Computer.Barred("win+r");
                acted.Clear();
                Security.Pick(Security.Azure);
                Job azureKeys = scripted(keyScript, "open the run box");
                keyAzure = azureKeys.Run() + " [" + string.Join(",", acted.ToArray()) + "] " + azureKeys.Asking;
                keyAzureYes = azureKeys.Run() + " [" + string.Join(",", acted.ToArray()) + "]";
                acted.Clear();''',
"Azure key confirmation test")
capri_replace(r'''                // What each kind of step needs: an asked-for send needs toggle 7, buying 8, and anything unmentioned 9 as well.
                Security.Pick(Security.Trusted);
                Job sam = new Job("message Sam hi on Discord"), hoodie = new Job("buy the blue hoodie"), browse = new Job("search the shop for hoodies");
                bool trusted = !sam.Needs("send") && sam.Needs("delete") && hoodie.Needs("buy") && browse.Needs("buy") && sam.Needs("keys") && Computer.Barred("win+r") && Computer.Risk("press", new ToolArguments { Keys = "win+r" }, chat) == "keys";
                Security.Set(Security.Pays, true);
                bool pays = !hoodie.Needs("buy") && browse.Needs("buy");
                Security.Set(Security.Unasked, true);
                bool unasked = !browse.Needs("buy") && !sam.Needs("delete") && !sam.Needs("keys") && !Computer.Barred("win+r");
                Security.Set(Security.Sends, false);
                bool sends = sam.Needs("send") && sam.Needs("delete") && !hoodie.Needs("buy");
                Security.Pick(Security.Lockdown);
                bool lockdown = sam.Needs("send") && hoodie.Needs("buy") && sam.Needs("keys");
                needsRight = trusted && pays && unasked && sends && lockdown;''',
r'''                // Sends can follow the user's request; payments and actions outside it always keep their separate approval gates.
                Computer.KeysOk = false;
                Security.Pick(Security.Trusted);
                Job sam = new Job("message Sam hi on Discord"), hoodie = new Job("buy the blue hoodie"), browse = new Job("search the shop for hoodies");
                bool trusted = !sam.Needs("send") && sam.Needs("delete") && hoodie.Needs("buy") && browse.Needs("buy") && sam.Needs("keys") && Computer.Barred("win+r") && Computer.Risk("press", new ToolArguments { Keys = "win+r" }, chat) == "keys";
                Security.Set(Security.Pays, true);
                bool pays = hoodie.Needs("buy") && browse.Needs("buy") && Security.Locked(Security.Pays) && !Security.On(Security.Pays);
                Security.Set(Security.Unasked, true);
                bool unasked = browse.Needs("buy") && sam.Needs("delete") && sam.Needs("keys") && Computer.Barred("win+r") && Security.Locked(Security.Unasked) && !Security.On(Security.Unasked);
                Security.Set(Security.Sends, false);
                bool sends = sam.Needs("send") && sam.Needs("delete") && hoodie.Needs("buy");
                Security.Pick(Security.Lockdown);
                bool lockdown = sam.Needs("send") && hoodie.Needs("buy") && sam.Needs("keys");
                needsRight = trusted && pays && unasked && sends && lockdown;''',
"fixed action requirement tests")

capri_span('            if (keyAsked != ',
           '            // The window:',
r'''            if (keyAsked != "Should I press win+r? [] True" || keyYes != "Opened the Run box. [press win+r]" || !keysFreed || keyAzure != "Should I press win+r? [] True" || keyAzureYes != "Opened the Run box. [press win+r]" || Computer.Bypass) throw new Exception("Win + R must still ask first under Azure: " + keyAsked + " / " + keyYes + " / " + keyAzure + " / " + keyAzureYes + " / " + keysFreed);
            if (passwordTrusted != Computer.SignInYourself || passwordOn != Computer.SignInYourself) throw new Exception("Passwords must stay theirs to type even after a legacy toggle attempt: " + passwordTrusted + " / " + passwordOn);
            if (!needsRight) throw new Exception("SECURITY's job safeguards went wrong: " + string.Join(" / ", wrong.ToArray()));
            checks.Add("PASS SECURITY in her jobs: requested sends can run, payments and unrequested actions always ask, Win + R asks under both Trusted and Azure, and sign-in fields always stay for the user to fill in");

''',
"Azure job result assertions")

capri_replace(r'''            mainframe.SlideSecurity(Security.Blackwall);
            string walled = mainframe.SecurityShown;
            bool walledHey = HeyCapriOn, walledSettings = mainframe.BlackwallStatus == "Security: Blackwall | She never asks, and listens for Hey Capri.";''',
r'''            mainframe.SlideSecurity(Security.Azure);
            string walled = mainframe.SecurityShown;
            bool walledHey = HeyCapriOn, walledSettings = mainframe.AzureStatus == "Security: Azure | Normal actions on; sensitive actions stay protected.";''',
"Security sheet Azure state")
capri_replace(r'''            if (opened == null || !opened.StartsWith("Trusted | Trusted | 1111111000001 | She does what you ask", StringComparison.Ordinal) || !flipped.StartsWith("Custom | Trusted | 0111111000001 | Your own mix", StringComparison.Ordinal) || flippedSaved != "0111111000"
                || !tapped.StartsWith("Trusted | Trusted | 1111111000001", StringComparison.Ordinal) || !locked.StartsWith("Lockdown | Lockdown | 0000000000001 | She asks first before she does anything", StringComparison.Ordinal) || !walled.StartsWith("Blackwall | Blackwall | 1111111111100 | She never asks", StringComparison.Ordinal) || !walledHey || !walledSettings || HeyCapriOn)
                throw new Exception("The SECURITY window went wrong: " + opened + " // " + flipped + " // " + tapped + " // " + locked + " // " + walled + " // " + walledSettings);
            if (!friendRow) throw new Exception("The SECURITY friend request row did not toggle and save.");
            if (crowded != null || at100 != null || at150 != null || at200 != null) throw new Exception("The SECURITY window's layout doesn't fit: " + crowded + " / 100% " + at100 + " / 150% " + at150 + " / 200% " + at200);
            checks.Add("PASS SECURITY window: Settings > HABITS opens it on Trusted; a toggle click makes it Custom and saves, a click on the slider puts Trusted back, sliding to Lockdown or Blackwall sets every toggle (and \"Hey Capri\") and Settings follows; at 100%, 150% and 200% nothing overlaps, pokes out or gets cut off (security-100.png, security-150.png, security-200.png)");''',
r'''            if (opened == null || !opened.StartsWith("Trusted | Trusted | 1111111000001 | She does what you ask", StringComparison.Ordinal) || !flipped.StartsWith("Custom | Trusted | 0111111000001 | Your own mix", StringComparison.Ordinal) || flippedSaved != "0111111000"
                || !tapped.StartsWith("Trusted | Trusted | 1111111000001", StringComparison.Ordinal) || !locked.StartsWith("Lockdown | Lockdown | 0000000000001 | She asks first before she does anything", StringComparison.Ordinal) || !walled.StartsWith("Azure | Azure | 1111111000101 | Normal desktop actions are enabled; sensitive actions still need your confirmation.", StringComparison.Ordinal) || !walledHey || !walledSettings || HeyCapriOn)
                throw new Exception("The SECURITY window went wrong: " + opened + " // " + flipped + " // " + tapped + " // " + locked + " // " + walled + " // " + walledSettings);
            if (!friendRow) throw new Exception("The SECURITY friend request row did not toggle and save.");
            if (crowded != null || at100 != null || at150 != null || at200 != null) throw new Exception("The SECURITY window's layout doesn't fit: " + crowded + " / 100% " + at100 + " / 150% " + at150 + " / 200% " + at200);
            checks.Add("PASS SECURITY window: Settings > HABITS opens it on Trusted; a toggle click makes it Custom and saves, a click on the slider puts Trusted back, sliding to Lockdown or Azure updates the safe toggles and optional wake word; at 100%, 150% and 200% nothing overlaps, pokes out or gets cut off (security-100.png, security-150.png, security-200.png)");''',
"Security sheet assertions")

capri_replace(r'''                // Each preset: on in Lockdown, Guarded and Trusted, off in Blackwall, and their saves read as they did before it.
                System.Collections.Generic.List<string> wrong = new System.Collections.Generic.List<string>();
                for (int preset = Security.Lockdown; preset <= Security.Blackwall; preset++)
                {
                    Security.Pick(preset);
                    if (Security.On(Security.Personal) != (preset != Security.Blackwall) || Security.Preset != preset || Security.Saved.Length != 10 || preferences.Permissions != Security.Saved)
                        wrong.Add(Security.Presets[preset] + " " + Security.On(Security.Personal) + " saved " + preferences.Permissions);
                }
                // Flipped away from its preset's default it makes Custom and saves a 12th mark, read back as it was.
                Security.Pick(Security.Trusted);
                Security.Set(Security.Personal, false);
                bool trustedOff = Security.Preset == Security.Custom && preferences.Permissions == "111111100000";
                Security.Load(preferences.Permissions);
                trustedOff &= !Security.On(Security.Personal) && Security.Preset == Security.Custom;
                Security.Set(Security.Personal, true);
                trustedOff &= Security.Preset == Security.Trusted && preferences.Permissions == "1111111000";
                Security.Pick(Security.Blackwall);
                Security.Set(Security.Personal, true);
                bool blackwallOn = Security.Preset == Security.Custom && preferences.Permissions == "111111111101";
                Security.Load(preferences.Permissions);
                blackwallOn &= Security.On(Security.Personal) && Security.On(Security.Secrets) && !Security.On(Security.Friends);
                // The old Blackwall switch sets toggles 1 to 10 and leaves this one alone.
                Security.Pick(Security.Trusted);
                Computer.Bypass = true;
                bool switchLeaves = Security.On(Security.Personal);
                Computer.Bypass = false;
                switchLeaves &= Security.On(Security.Personal) && Security.Preset == Security.Trusted;
                // Saves from before it get their preset's default: off for Blackwall's ten toggles, on for anything else.
                DataContractJsonSerializer json = new DataContractJsonSerializer(typeof(Preferences));
                Preferences wasBlackwall = (Preferences)json.ReadObject(new MemoryStream(System.Text.Encoding.UTF8.GetBytes("{\"Bypass\":true,\"Size\":240}")));
                Migrate(wasBlackwall);
                string olderSaves = "";
                foreach (string older in new[] { "0000000000", "1110000000", "1111111000", "0111111000", "01111110001", wasBlackwall.Permissions, "1111111111", null, "not toggles" })
                {
                    Security.Load(older);
                    olderSaves += (Security.On(Security.Personal) ? "1" : "0");
                }
                Security.Load(securityWas);
                if (wrong.Count > 0 || !trustedOff || !blackwallOn || !switchLeaves || olderSaves != "111110011")
                    throw new Exception("Keep personal details out of her memories went wrong in SECURITY: " + string.Join(" / ", wrong.ToArray()) + " / Trusted off " + trustedOff + " / Blackwall on " + blackwallOn + " / old switch " + switchLeaves + " / older saves " + olderSaves);
                checks.Add("PASS SECURITY's Keep personal details out of her memories: on in Lockdown, Guarded and Trusted and off in Blackwall, with their saves as they were; turned the other way it's Custom and saves a 12th mark that reads back; the old Blackwall switch leaves it alone; and a save from before it gets it off for Blackwall's ten toggles and on for every other");''',
r'''                // Every preset keeps personal details out of memories by default, including Azure.
                System.Collections.Generic.List<string> wrong = new System.Collections.Generic.List<string>();
                for (int preset = Security.Lockdown; preset <= Security.Azure; preset++)
                {
                    Security.Pick(preset);
                    if (!Security.On(Security.Personal) || Security.Preset != preset || Security.Saved.Length != 10 || preferences.Permissions != Security.Saved)
                        wrong.Add(Security.Presets[preset] + " " + Security.On(Security.Personal) + " saved " + preferences.Permissions);
                }
                // Turning the personal-data safeguard off makes a Custom preset and writes its extra mark.
                Security.Pick(Security.Azure);
                Security.Set(Security.Personal, false);
                bool azureOff = Security.Preset == Security.Custom && preferences.Permissions == "111111100000";
                Security.Load(preferences.Permissions);
                azureOff &= !Security.On(Security.Personal) && Security.Preset == Security.Custom;
                Security.Set(Security.Personal, true);
                azureOff &= Security.On(Security.Personal) && Security.Preset == Security.Azure && preferences.Permissions == "1111111000";
                Security.Pick(Security.Azure);
                bool azureRestored = Security.Preset == Security.Azure && Security.On(Security.Personal);
                // Legacy bypass writes are ignored and cannot change the selected safe preset or privacy setting.
                Computer.Bypass = true;
                bool legacyBypassDisabled = !Computer.Bypass && Security.Preset == Security.Azure && Security.On(Security.Personal);
                Computer.Bypass = false;
                legacyBypassDisabled &= !Computer.Bypass && Security.Preset == Security.Azure && Security.On(Security.Personal);
                // Old all-on permission saves have restricted bits stripped and retain the privacy safeguard.
                DataContractJsonSerializer json = new DataContractJsonSerializer(typeof(Preferences));
                Preferences wasLegacy = (Preferences)json.ReadObject(new MemoryStream(System.Text.Encoding.UTF8.GetBytes("{\"Bypass\":true,\"Size\":240}")));
                Migrate(wasLegacy);
                string olderSaves = "";
                foreach (string older in new[] { "0000000000", "1110000000", "1111111000", "0111111000", "01111110001", wasLegacy.Permissions, "1111111111", null, "not toggles" })
                {
                    Security.Load(older);
                    olderSaves += (Security.On(Security.Personal) ? "1" : "0");
                }
                Security.Load(securityWas);
                if (wrong.Count > 0 || !azureOff || !azureRestored || !legacyBypassDisabled || olderSaves != "111111111")
                    throw new Exception("Keep personal details out of her memories went wrong in SECURITY: " + string.Join(" / ", wrong.ToArray()) + " / Azure off " + azureOff + " / Azure restored " + azureRestored + " / legacy bypass " + legacyBypassDisabled + " / old saves " + olderSaves);
                checks.Add("PASS SECURITY's Keep personal details out of her memories: on in every preset including Azure; turning it off makes a Custom save that reads back; legacy bypass writes cannot change the preset; old permission saves keep personal data protected");''',
"privacy preset tests")

capri_replace("                // Off, as in Blackwall: Get to know me's answers and what she saw are kept as they are, and her notes keep only their",
              "                // Off, when the user disables it: Get to know me's answers and what she saw are kept as they are, and her notes keep only their",
              "privacy comment")
capri_replace(r'''                checks.Add("PASS a form's personal boxes: with Keep personal details out of her memories on, a card number, an email and a street address reach her jobs as (value hidden) while an ordinary box and an empty card box read as they are; off, as in Blackwall, she reads all three");''',
              r'''                checks.Add("PASS a form's personal boxes: with Keep personal details out of her memories on, a card number, an email and a street address reach her jobs as (value hidden) while an ordinary box and an empty card box read as they are; when the user disables it, she reads all three");''',
              "privacy form description")
capri_replace("                mainframe.SlideSecurity(Security.Blackwall);","                mainframe.SlideSecurity(Security.Azure);","privacy sheet preset")
capri_replace(r'''                if (opened == null || !opened.StartsWith("Trusted | Trusted | 1111111000001", StringComparison.Ordinal) || !flipped.StartsWith("Custom | Trusted | 1111111000000 | Your own mix", StringComparison.Ordinal) || flippedSaved != "111111100000"
                    || !back.StartsWith("Trusted | Trusted | 1111111000001", StringComparison.Ordinal) || !walled.StartsWith("Blackwall | Blackwall | 1111111111100", StringComparison.Ordinal) || !locked.StartsWith("Lockdown | Lockdown | 0000000000001 | She asks first before she does anything on your PC.", StringComparison.Ordinal)
                    || crowded != null || at100 != null || at150 != null || at200 != null)
                    throw new Exception("The SECURITY window's 13th row went wrong: " + opened + " // " + flipped + " (" + flippedSaved + ") // " + back + " // " + walled + " // " + locked + " // fit " + crowded + " / 100% " + at100 + " / 150% " + at150 + " / 200% " + at200);
                checks.Add("PASS SECURITY window's 13th row: Keep personal details out of her memories sits under HER MEMORY, on for Trusted and Lockdown and off for Blackwall; a click makes it Custom and saves, a second puts Trusted back; and at 100%, 150% and 200% nothing overlaps, pokes out or gets cut off (security-privacy-100.png, security-privacy-150.png, security-privacy-200.png)");''',
r'''                if (opened == null || !opened.StartsWith("Trusted | Trusted | 1111111000001", StringComparison.Ordinal) || !flipped.StartsWith("Custom | Trusted | 1111111000000 | Your own mix", StringComparison.Ordinal) || flippedSaved != "111111100000"
                    || !back.StartsWith("Trusted | Trusted | 1111111000001", StringComparison.Ordinal) || !walled.StartsWith("Azure | Azure | 1111111000101 | Normal desktop actions are enabled; sensitive actions still need your confirmation.", StringComparison.Ordinal) || !locked.StartsWith("Lockdown | Lockdown | 0000000000001 | She asks first before she does anything on your PC.", StringComparison.Ordinal)
                    || crowded != null || at100 != null || at150 != null || at200 != null)
                    throw new Exception("The SECURITY window's 13th row went wrong: " + opened + " // " + flipped + " (" + flippedSaved + ") // " + back + " // " + walled + " // " + locked + " // fit " + crowded + " / 100% " + at100 + " / 150% " + at150 + " / 200% " + at200);
                checks.Add("PASS SECURITY window's 13th row: Keep personal details out of her memories stays on for Azure and every other preset; a click makes it Custom and saves, a second puts Trusted back; and at 100%, 150% and 200% nothing overlaps, pokes out or gets cut off (security-privacy-100.png, security-privacy-150.png, security-privacy-200.png)");''',
"privacy sheet assertions")

capri_replace('            Section(checks, "SmokeCapriCodes", delegate { SmokeCapriCodes(checks); });',
              '            Section(checks, "SmokeLegacyAccessCodes", delegate { SmokeLegacyAccessCodes(checks); });',
              "legacy access-code test registration")
capri_span("        private void SmokeCapriCodes(System.Collections.Generic.List<string> checks)",
           "        internal void StartSmokeTest(string output, SmokeOptions options)",
r'''        private void SmokeLegacyAccessCodes(System.Collections.Generic.List<string> checks)
        {
            const string legacy = "CAPRI-0123-4567-89AB-CDEF";
            Cloud legacyCloud = new Cloud(legacy, "claude-sonnet-5-5");
            Cloud realKey = new Cloud("sk-ant-test", "claude-sonnet-5-5");
            if (Cloud.KindOf(legacy) != null || legacyCloud.Kind != null || legacyCloud.Claude
                || realKey.Kind != "anthropic" || !realKey.Claude || realKey.Model != "claude-sonnet-5-5"
                || Brain.ClaudeAddress(realKey.Key, "/messages") != Brain.Anthropic + "/v1/messages")
                throw new Exception("A legacy Capri access-code string was treated as a provider, or a user's Anthropic key changed.");
            checks.Add("PASS legacy Capri access-code strings are not recognized as providers; user-supplied Anthropic keys retain their model and use Anthropic directly");
        }

''',
"replace obsolete access-code test")

capri_replace("            if (Cloud.IsCode(key)) key = key.ToUpperInvariant();\n", "", "remove legacy key normalization")
capri_replace("            if (brain.Remote != null && brain.Remote.Code) return brain.Remote.CodeNote;\n", "", "remove custom model access-code restriction")
capri_replace("                foreach (int preset in new[] { Security.Lockdown, Security.Guarded, Security.Trusted, Security.Blackwall })",
              "                foreach (int preset in new[] { Security.Lockdown, Security.Guarded, Security.Trusted, Security.Azure })",
              "friend preset references")
capri_replace("                    if (LookContrast(Mainframe.BlackwallInk, Neon.Field) < 4.5) throw new Exception(Neon.LookNames[look] + \"\'s Blackwall name is hard to read on its box.\");",
              "                    if (LookContrast(Mainframe.AzureInk, Neon.Field) < 4.5) throw new Exception(Neon.LookNames[look] + \"\'s Azure name is hard to read on its box.\");",
              "Azure contrast color")

capri_span("                            bool bypassWas = Computer.Bypass;",
           "                            SecurityChecks(checks, output);",
r'''                            Job payJob = new Job("play lofi on youtube"), sendingJob = new Job("message Sam hi on Discord");
                            Security.Pick(Security.Trusted);
                            Computer.KeysOk = false;
                            bool checksPay = !Computer.Needless("Should I pay $5 for it?") && !Computer.Needless("It's $4.99. Buy it?") && !Computer.Needless("Book the 7:30 table at Nobu?") && !Computer.Needless("Reserve it?") && !Computer.Needless("Place bid?") && payJob.Needs("buy") && !sendingJob.Needs("send") && Computer.Allowing(Computer.Prompt) == Computer.Prompt
                                && Computer.Barred("ctrl+shift+esc") && (Computer.Tools + Computer.ClaudeTools + Computer.Listing).Split(new[] { "before a step that buys or pays" }, StringSplitOptions.None).Length == 4;
                            string safePrompt = Computer.Allowing(Computer.Prompt), safeSeeing = Computer.Allowing(Computer.Seeing);
                            Computer.Bypass = true;
                            bool legacyBypassDisabled = !Computer.Bypass && Security.Preset == Security.Trusted && Computer.Allowing(Computer.Prompt) == safePrompt && Computer.Allowing(Computer.Seeing) == safeSeeing;
                            Security.Pick(Security.Azure);
                            bool azureProtected = Security.Preset == Security.Azure && !Computer.Bypass
                                && Security.Locked(Security.Pays) && Security.Locked(Security.Unasked) && Security.Locked(Security.Secrets)
                                && !Security.On(Security.Pays) && !Security.On(Security.Unasked) && !Security.On(Security.Secrets)
                                && payJob.Needs("buy") && Computer.Barred("win+r")
                                && !Computer.Needless("Should I pay $5 for it?") && !Computer.Needless("It's $4.99. Buy it?");
                            Security.Pick(Security.Trusted);
                            if (!checksPay || !legacyBypassDisabled || !azureProtected
                                || safePrompt.IndexOf("Never type passwords", StringComparison.Ordinal) < 0 || safePrompt.IndexOf("Always call ask before you buy or pay for anything.", StringComparison.Ordinal) < 0
                                || safeSeeing.IndexOf("Never type passwords", StringComparison.Ordinal) < 0 || safeSeeing.IndexOf("stop and ask", StringComparison.Ordinal) < 0
                                || safePrompt.IndexOf("Bypass all permissions", StringComparison.Ordinal) >= 0 || safeSeeing.IndexOf("Bypass all permissions", StringComparison.Ordinal) >= 0)
                                throw new Exception("Fixed security safeguards went wrong: payments " + checksPay + ", legacy bypass disabled " + legacyBypassDisabled + ", Azure protected " + azureProtected);
                            checks.Add("PASS fixed security safeguards: payments and purchases always require confirmation, unrequested actions still ask, credentials remain user-entered, and the legacy bypass flag cannot relax any of them");
                            bool cursorShown = mainframe.JobsStatus == "cursor | Security: Trusted";
                            Security.Pick(Security.Azure);
                            bool azureShown = mainframe.JobsStatus == "cursor | Security: Azure" && !Computer.Bypass && !Security.On(Security.Pays) && !Security.On(Security.Unasked) && !Security.On(Security.Secrets);
                            Security.Pick(Security.Trusted);
                            ToggleCursor();
                            bool quickShown = mainframe.JobsStatus == "- | Security: Trusted" && !UsesCursor;
                            ToggleCursor();
                            bool azureNamed = mainframe.AzureStatus == "Security: Trusted | Asks before paying or what you didn't say.";
                            if (!cursorShown || !azureShown || !quickShown || !azureNamed || Computer.Bypass || !UsesCursor || HeyCapriOn) throw new Exception("The Use her cursor and SECURITY switches went wrong: " + mainframe.JobsStatus + " / " + mainframe.AzureStatus);
                            checks.Add("PASS Settings: Use her cursor starts on, and SECURITY under HABITS shows Trusted with its confirmation summary; Azure remains a safe preset with fixed payment, unrequested-action and credential protections");
                            SecurityChecks(checks, output);''',
"replace unrestricted bypass tests")


capri_span("                                    // Under Bypass she types passwords too, and they only ever show as dots.",
           "                                finally\n                                {\n                                    Computer.Look = oldLook;",
r'''                                    // The legacy bypass cannot authorize credential entry or purchases.
                                    bool legacyBypassWas = Computer.Bypass;
                                    Func<bool> secretWas = Computer.SecretFocus;
                                    Sight loginSight = new Sight { Window = new IntPtr(7), Title = "Sign in", Program = "game" };
                                    loginSight.Targets.Add(new Target { Number = 1, Role = "box", Name = "Password", Secret = true, Line = true, Box = new Rectangle(10, 10, 200, 20) });
                                    string passwordResult, passwordSummary, passwordLabel, buyRun;
                                    int buyLine = 0, buyActs = 0;
                                    Func<string, ToolArguments, Sight, string> actWas = Computer.Act;
                                    try
                                    {
                                        Computer.Bypass = true;
                                        Computer.SecretFocus = delegate { return false; };
                                        Computer.Look = delegate { return loginSight; };
                                        Computer.Front = delegate { return new IntPtr(7); };
                                        passwordResult = Computer.Do("type", new ToolArguments { Target = "1", Text = "hunter2!!" }, loginSight);
                                        Computer.Keep("hunter2!!");
                                        passwordSummary = Hands.Hush("my password is hunter2!!");
                                        passwordLabel = Computer.Moving("type", Computer.Masked(new ToolArguments { Text = "hunter2!!\n" }), null, false);
                                        Sight hatShop = new Sight { Window = new IntPtr(7), Title = "Cat hat", Program = "shop" };
                                        hatShop.Targets.Add(new Target { Number = 1, Role = "button", Name = "Buy now", Box = new Rectangle(10, 40, 80, 20) });
                                        Computer.Look = delegate { return hatShop; };
                                        Computer.Act = delegate(string name, ToolArguments a, Sight sight) { buyActs++; return "Clicked it."; };
                                        string[] buyScript = { "ask{\"text\": \"It's $4.99. Buy it?\"}", "click{\"target\": \"1\"}", "done{\"text\": \"Bought the cat hat.\"}" };
                                        Job hatJob = new Job("buy the cat hat");
                                        hatJob.Think = delegate(string system, string user, System.Collections.Generic.List<System.Collections.Generic.KeyValuePair<string, ToolArguments>> calls) { return buyScript[Math.Min(buyLine++, buyScript.Length - 1)]; };
                                        buyRun = hatJob.Run();
                                    }
                                    finally
                                    {
                                        Computer.Bypass = legacyBypassWas;
                                        Computer.SecretFocus = secretWas;
                                        Computer.Act = actWas;
                                    }
                                    if (Computer.Bypass || passwordResult != "Won't type in a password box. They type passwords themselves." || passwordResult.IndexOf("hunter2", StringComparison.Ordinal) >= 0
                                        || passwordSummary != "my password is " + Computer.Dots || passwordLabel != "Typing \"" + Computer.Dots + "\" and pressing Enter")
                                        throw new Exception("Passwords were not kept user-entered and masked: " + passwordResult + " / " + passwordSummary + " / " + passwordLabel);
                                    checks.Add("PASS credentials stay user-entered: the legacy bypass flag has no effect, password fields refuse automation, and password text is masked in summaries and task labels");
                                    if (buyRun != "It's $4.99. Buy it?" || buyLine != 1 || buyActs != 0)
                                        throw new Exception("A purchase question was suppressed or the purchase proceeded without confirmation: " + buyRun + " after " + buyLine + " steps / actions " + buyActs);
                                    checks.Add("PASS purchase confirmation: a job's \"It's $4.99. Buy it?\" reaches the user and the Buy button is not pressed before approval");
''',
           "replace legacy password and purchase bypass tests")

capri_span("                                    // Blackwall mode: the card is theirs to give, so she types it and asks for one in her own words.",
           "                                    Sight detailsSight = new Sight",
r'''                                    // Legacy bypass writes cannot authorize card entry; the user supplies card details.
                                    bool legacyCardBypassWas = Computer.Bypass;
                                    int cardActs = 0;
                                    string cardResult, cardAsk;
                                    Func<string, ToolArguments, Sight, string> cardActWas = Computer.Act;
                                    try
                                    {
                                        Computer.Bypass = true;
                                        for (int i = 0; i < 3; i++) paySight.Targets[i].Value = null;
                                        Computer.Look = delegate { return paySight; };
                                        Computer.Act = delegate(string name, ToolArguments a, Sight sight) { cardActs++; return "Typed it."; };
                                        string[] cardScript = { "type{\"target\": \"1\", \"text\": \"4111 1111 1111 1111\"}", "done{\"text\": \"Put your card in.\"}" };
                                        int cardLine = 0;
                                        Job carding = new Job("pay for the flight with my card 4111 1111 1111 1111");
                                        carding.Think = delegate(string system, string user, System.Collections.Generic.List<System.Collections.Generic.KeyValuePair<string, ToolArguments>> calls) { return cardScript[Math.Min(cardLine++, cardScript.Length - 1)]; };
                                        cardResult = carding.Run();
                                        Job cardAsking = new Job("book the cheapest flight from Sydney to Melbourne on 14 November for Alex Chen");
                                        cardAsking.Think = delegate(string system, string user, System.Collections.Generic.List<System.Collections.Generic.KeyValuePair<string, ToolArguments>> calls) { return "ask{\"text\": \"What's your card number?\"}"; };
                                        cardAsk = cardAsking.Run();
                                    }
                                    finally
                                    {
                                        Computer.Bypass = legacyCardBypassWas;
                                        Computer.Act = cardActWas;
                                    }
                                    if (Computer.Bypass || cardActs != 0 || cardResult.IndexOf("I don't type card numbers", StringComparison.Ordinal) < 0 || cardAsk != Computer.PayYourself)
                                        throw new Exception("Card details were not kept user-entered: " + cardActs + " / " + cardResult + " / " + cardAsk);
                                    checks.Add("PASS card details stay user-entered: legacy bypass writes cannot type a card number, and requests for card details hand the page back to the user");
''',
           "replace legacy card-entry bypass test")

capri_replace('                Security.Load("1111111111");\n                if (Security.On(Security.Friends) || !Security.On(Security.Secrets)) throw new Exception("Old SECURITY settings opted into friend requests or lost their old bits.");',
              '                Security.Load("1111111111");\n                if (Security.On(Security.Friends) || Security.On(Security.Secrets) || !Security.Locked(Security.Secrets)) throw new Exception("Old SECURITY settings opted into friend requests or restored a restricted permission.");',
              "old saved security permissions keep restricted bits locked")

s = s.replace("Security.Blackwall", "Security.Azure")
s = s.replace("mainframe.BlackwallStatus", "mainframe.AzureStatus")
s = s.replace("Mainframe.BlackwallInk", "Mainframe.AzureInk")
if any(x in s for x in ["Security.Blackwall", "BlackwallStatus", "BlackwallInk", "Cloud.IsCode", "CodeNote", "ReadCode", "Brain.Codes", "SmokeCapriCodes", "ToggleBypass", "Bypassing", "keyBlackwall"]):
    raise RuntimeError("Obsolete security or access-code symbols remain in app/Capri.cs")
if s.count("CAPRI-") != 1:
    raise RuntimeError("Expected exactly one inert legacy access-code regression-test literal")
p.write_text(s, encoding="utf-8")

replace_once("app/Computer.cs",
    "        // Legacy compatibility only: unrestricted permission bypass is permanently disabled.\n        internal static bool Bypass { get { return false; } set { Security.Jobs(false); } }",
    "        // Legacy compatibility only: unrestricted permission bypass is permanently disabled and writes are ignored.\n        internal static bool Bypass { get { return false; } set { } }",
    "make legacy bypass setter inert")


replace_once("app/Computer.cs",
    "        // Card number, expiry and security code boxes are theirs to fill, like password boxes, unless Type passwords and card numbers is on.",
    "        // Card number, expiry and security code boxes are always filled by the user, like password boxes.",
    "document fixed card-entry rule")
replace_once("app/Computer.cs",
    "                    // With Type passwords and card numbers on (Azure) she types them herself, so her own question about them reaches them as she wrote it.",
    "                    // Credentials are always user-entered, so her own question about them reaches them as she wrote it.",
    "document fixed credential rule in job ask")
replace_once("app/Computer.cs",
    "            // Type passwords and card numbers on (Azure): the card is theirs to give, so she types it when their job does.",
    "            // Card details are always user-entered; refuse any attempt to type into a card field.",
    "document fixed card-entry rule in tool execution")
replace_once("app/Computer.cs",
    "                    if (tool == \"ask\" && !Security.On(Security.Secrets) && Computer.AsksToSignIn(said, sight)) return End(\"asked\", Computer.SignInYourself);",
    "                    if (tool == \"ask\" && Computer.AsksToSignIn(said, sight)) return End(\"asked\", Computer.SignInYourself);",
    "always hand sign-in to the user")
replace_once("app/Computer.cs",
    "                    if (tool == \"ask\" && !Security.On(Security.Secrets) && Computer.AsksForCard(said)) return End(\"asked\", Computer.PaymentPage(sight) ? Computer.PayYourself : Computer.CardYourself);",
    "                    if (tool == \"ask\" && Computer.AsksForCard(said)) return End(\"asked\", Computer.PaymentPage(sight) ? Computer.PayYourself : Computer.CardYourself);",
    "always hand card requests to the user")
replace_once("app/Computer.cs",
    "                    if (!Security.On(Security.Secrets) && Computer.PaymentPage(sight) && !Paid())",
    "                    if (Computer.PaymentPage(sight) && !Paid())",
    "always hand payment pages to the user")
replace_once("app/Computer.cs",
    "            else if (tool == \"type\" && !Security.On(Security.Secrets) && Computer.CardBox(sight == null ? null : sight.Find(args.Target)))",
    "            else if (tool == \"type\" && Computer.CardBox(sight == null ? null : sight.Find(args.Target)))",
    "always refuse card-field typing")
replace_once("app/Computer.cs",
    "                if (danger == \"buy\" && !Security.On(Security.Secrets) && sight != null && sight.Targets.Exists(found => Computer.CardBox(found) && string.IsNullOrEmpty(found.Value))) return End(\"asked\", Computer.PayYourself);",
    "                if (danger == \"buy\" && sight != null && sight.Targets.Exists(found => Computer.CardBox(found) && string.IsNullOrEmpty(found.Value))) return End(\"asked\", Computer.PayYourself);",
    "always require user card entry at payment page")

replace_once("app/Brain.cs",
r'''        internal readonly string Host;
        internal readonly bool Code;
        private volatile string model;
        internal string Model { get { return Code ? Brain.Fastest : model; } set { model = Code ? Brain.Fastest : value; } }
        internal Cloud(string key, string model) { Code = false; Key = key; Kind = KindOf(Key); Model = model; }''',
r'''        internal readonly string Host;
        private volatile string model;
        internal string Model { get { return model; } set { model = value; } }
        internal Cloud(string key, string model) { Key = key; Kind = KindOf(Key); Model = model; }''',
"remove dead Cloud.Code field")
replace_once("app/Brain.cs",
    "        private bool CurrentCode { get { Cloud remote = Remote; return remote != null && remote.Code; } }\n\n",
    "",
    "remove CurrentCode")
replace_once("app/Brain.cs",
    "        private ThinkingPick CurrentPick { get { return Picked(CurrentKind, CurrentModel, CurrentCode); } }",
    "        private ThinkingPick CurrentPick { get { return Picked(CurrentKind, CurrentModel, false); } }",
    "remove CurrentCode from picker")
replace_once("app/Brain.cs",
r'''        internal bool ThinkingOpen { get { return ThinkingLevels.Closed(CurrentKind, CurrentCode) == null && !string.IsNullOrEmpty(CurrentModel); } }
        internal int ThinkingLevel { get { return Usable(CurrentPick, CurrentKind, CurrentModel); } }
        internal string ThinkingWhy(int level) { return LevelWhy(CurrentKind, CurrentModel, level, CurrentCode); }''',
r'''        internal bool ThinkingOpen { get { return ThinkingLevels.Closed(CurrentKind, false) == null && !string.IsNullOrEmpty(CurrentModel); } }
        internal int ThinkingLevel { get { return Usable(CurrentPick, CurrentKind, CurrentModel); } }
        internal string ThinkingWhy(int level) { return LevelWhy(CurrentKind, CurrentModel, level, false); }''',
"remove CurrentCode from thinking UI")
replace_once("app/Brain.cs", "Picked(remote.Kind, remote.Model, remote.Code)", "Picked(remote.Kind, remote.Model, false)", "remove Code from OpenAI picker")
replace_once("app/Brain.cs", "Picked(remote.Kind, model, remote.Code)", "Picked(remote.Kind, model, false)", "remove Code from Anthropic picker")
replace_once("app/Brain.cs",
    "return remote != null && !remote.Code && Drives && !noFastest && noAdvisor != remote.Key + remote.Model;",
    "return remote != null && Drives && !noFastest && noAdvisor != remote.Key + remote.Model;",
    "remove Code advisor exclusion")
replace_once("app/Brain.cs",
    "advising = !remote.Code && (answered || (fast && model == Fastest && Advises));",
    "advising = answered || (fast && model == Fastest && Advises);",
    "remove Code advisor request exclusion")

brain = Path("app/Brain.cs").read_text(encoding="utf-8")
for obsolete in ["remote.Code", "CurrentCode", "CodeNote", "capri-code", "capri-reactions", "Brain.Codes"]:
    if obsolete in brain:
        raise RuntimeError(f"Obsolete access-code implementation remains in app/Brain.cs: {obsolete}")


computer = Path("app/Computer.cs").read_text(encoding="utf-8")
if "Security.On(Security.Secrets)" in computer:
    raise RuntimeError("A credential safety gate still depends on the removed Secrets toggle in app/Computer.cs")

print("Azure source patch applied.")
print("Changed files: app/Capri.cs, app/Computer.cs, app/Brain.cs")
