
class Version:
    def __init__(self):
        self.FILE_WITH_VERSION_INFORMATION = "version"
        self.version_increment()

    def version_increment(self):
        # Read the data from the last version file
        fin = open(self.FILE_WITH_VERSION_INFORMATION, "rt")
        data = fin.read()
        fin.close()

        prev_version = "0.0.0.0"

        for item in data.split("\n"):
            if "FileVersion" in item:
                prev_version = item.replace("StringStruct(u\'FileVersion\', u\'", "").replace("\'),", "").strip()

        ver = str(prev_version).split('.')
        new_version = (ver[0] + '.' + ver[1] + '.' + ver[2] + '.' + str(int(ver[3]) + 1)).strip()

        prev_version_commas = prev_version.replace('.', ', ')
        new_version_commas = new_version.replace('.', ', ')

        data = data.replace(prev_version_commas, new_version_commas)
        data = data.replace(prev_version_commas, new_version_commas)
        data = data.replace(prev_version, new_version)
        data = data.replace(prev_version, new_version)

        # Write the data to the same file
        fin = open(self.FILE_WITH_VERSION_INFORMATION, "wt")
        fin.write(data)
        fin.close()

        print("Version updated to:", new_version)
