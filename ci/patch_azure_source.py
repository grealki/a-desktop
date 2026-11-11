from pathlib import Path

path = Path("app/Capri.cs")
source = path.read_text(encoding="utf-8")

old = """                    }
                    catch (Exception error)
                    {
                        TestFailed = true;
                        SmokeRun.StepFailed(step, error, checks);
                    }
                    finally { stepping = false; }"""

new = """                    }
                    }
                    catch (Exception error)
                    {
                        TestFailed = true;
                        SmokeRun.StepFailed(step, error, checks);
                    }
                    finally { stepping = false; }"""

matches = source.count(old)
if matches != 1:
    raise RuntimeError(f"Expected exactly one Windows smoke-test brace location, found {matches}")

path.write_text(source.replace(old, new, 1), encoding="utf-8")
