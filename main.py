import subprocess, sys, json, concurrent.futures, requests, os, hashlib, base64
solution_path = input("Please input a solution/project path to search for dependencies:\n")
output_path = input("Please choose an output path for the nugets:\n")
try:
    res = subprocess.Popen("dotnet list package --include-transitive --include-prerelease --format json", cwd=solution_path, stdout=subprocess.PIPE)
except:
    print("A Project or solution could not be found.")
    raise
out, err = res.communicate()
nugets = json.loads(out)
links = []
for project in nugets["projects"]:
    if "frameworks" in project:
        for framework in project["frameworks"]:
            if "topLevelPackages" in framework:
                for pkg in framework["topLevelPackages"]:
                    links.append({"id": pkg["id"], "ver": pkg["resolvedVersion"]})
            if "transitivePackages" in framework:
                for pkg in framework["transitivePackages"]:
                    links.append({"id": pkg["id"], "ver": pkg["resolvedVersion"]})


def makerequest(nuget):
    res = requests.get(f"https://www.nuget.org/api/v2/package/{nuget["id"]}/{nuget["ver"]}")
    path = os.path.join(output_path, f"{nuget["id"]}.nupkg")
    with open(path, "w+b") as f:
        f.write(res.content)
        md5 = base64.b64encode(hashlib.md5(res.content).digest()).decode()
        hash = res.headers.get("content-md5")
    if(md5 != hash):
        os.remove(path)
        fails = fails + 1
        return f"failed to download {nuget["id"]} - hash didnt match"
    success = success + 1
    return f"downloaded {nuget["id"]}"
success = 0
fails = 0
progress = 0
print("Downloading nugets (this may take a while)...")
with concurrent.futures.ThreadPoolExecutor() as threadpool:
    for x in threadpool.map(makerequest, links):
        progress = progress + 1
        print(f"{x}. {progress}/{len(links)}")
print(f"finished downloading {success} / {len(links)}. failed {fails}.")