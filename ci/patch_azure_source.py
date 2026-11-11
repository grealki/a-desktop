from pathlib import Path

path = Path("app/Capri.cs")
source = path.read_text(encoding="utf-8")

def replace_once(old, new, label):
    global source
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    source = source.replace(old, new, 1)

# Close the purchase-confirmation try block before its finally clause.
marker = "PASS purchase confirmation:"
start = source.find(marker)
if start < 0 or source.find(marker, start + len(marker)) >= 0:
    raise RuntimeError("Purchase-confirmation marker is missing or duplicated")
finally_marker = "\n                                finally"
finish = source.find(finally_marker, start)
if finish < 0:
    raise RuntimeError("Purchase-confirmation finally clause was not found")
source = source[:finish] + "\n                                }" + source[finish:]

# Undo the misplaced brace inserted by the previous attempted repair.
replace_once(
    "                    }\n                    }\n                    catch (Exception error)",
    "                    }\n                    catch (Exception error)",
    "StartSmokeTest catch block"
)

# Cloud.Code belonged only to the removed Capri access-code system.
replace_once(
    "            if (brain.Remote != null && brain.Remote.Code && name != Brain.Fastest) return;\n",
    "",
    "legacy model-selection lock"
)
replace_once(
    "                        else if (ticket == asking && remote != null && remote.Code && brain.Remote == remote) mainframe.ShowCloud(remote, cloudModels);\n",
    "",
    "legacy cloud-recovery branch"
)

path.write_text(source, encoding="utf-8")
