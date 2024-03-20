#  Generating the maximum list of metadata attribute names

with open("metadata/Packages", "r") as f:
    content = f.read()
    packages_list = content.split("\n\n")
    max_attributes = set()
    for package in packages_list:
        attrs = set(package.split("\n"))
        attrs = set(map(lambda attr: attr.split(": ")[0], attrs))
        max_attributes = attrs.union(max_attributes - attrs)

    max_attributes = list(map(lambda attr: attr + " VARCHAR(255),", max_attributes))
    max_attributes = list(map(lambda attr: attr.replace("-", "_"), max_attributes))

for attr in max_attributes:
    print(attr)

