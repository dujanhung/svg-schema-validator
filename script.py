from pathlib import Path
from lxml import etree
import cssutils
import sys
import urllib.request
import tempfile
RESTRICTED_TAGS={"defs","use","script","image","text"}
class Validator:
 def __init__(self,schema_source:str):
  self.schema=self.load_schema(schema_source)
 def load_schema(self,schema_source:str):
  try:
   if schema_source.startswith("http://") or schema_source.startswith("https://"):
    with urllib.request.urlopen(schema_source) as r:
     data=r.read()
    tmp=tempfile.NamedTemporaryFile(delete=False,suffix=".xsd")
    tmp.write(data)
    tmp.close()
    schema_path=tmp.name
   else:
    schema_path=schema_source
   tree=etree.parse(schema_path)
   return etree.XMLSchema(tree)
  except Exception as e:
   print(f"🔴 {schema_source}")
   print(e)
   sys.exit(1)
 def parse_svg(self,file_path:Path):
  try:
   parser=etree.XMLParser(remove_blank_text=True)
   return etree.parse(str(file_path),parser)
  except etree.XMLSyntaxError:
   return None
 def validate_svg(self,file_path:Path):
  result={"ok":True,"error":[]}
  tree=self.parse_svg(file_path)
  if tree is None:
   result["error"].append(f"[XML ERROR] {file_path}")
   result["ok"]=False
   return result
  root=tree.getroot()
  if self.schema is not None and not self.schema.validate(tree):
   for e in self.schema.error_log:
    result["error"].append(f"[SCHEMA ERROR] {file_path}: {e}")
   result["ok"]=False
  for element in root.iter():
   tag=etree.QName(element).localname
   if tag in RESTRICTED_TAGS:
    result["error"].append(f"[RESTRICTED] {file_path}: <{tag}>")
    result["ok"]=False
  for style in root.xpath("//*[local-name()='style']"):
   css_text=(style.text or "").strip()
   if not css_text:
    continue
   if "\n\n" in css_text:
    result["error"].append(f"[CSS EMPTY LINE] {file_path}")
    result["ok"]=False
   try:
    cssutils.parseString(css_text)
   except Exception as e:
    result["error"].append(f"[CSS ERROR] {file_path}: {e}")
    result["ok"]=False
  return result
def main():
 if len(sys.argv)<3:
  print("✨ usage")
  print(f"🪜 {sys.argv[0]} <schema.xsd|url> <file-or-directory...>")
  return 1
 validator=Validator(sys.argv[1])
 files=[]
 for arg in sys.argv[2:]:
  path=Path(arg)
  if path.is_file() and path.suffix==".svg":
   files.append(path)
  elif path.is_dir():
   files.extend(path.rglob("*.svg"))
 if not files:
  print("❓ no SVG files found")
  return 0
 failed=False
 count=0
 for file in files:
  result=validator.validate_svg(file)
  if result["ok"][count]:
   print(f"🟢 {file}")
  else:
   print(f"🔴 {file}")
   for e in result["error"][count]:
    print(f"🪜 {e}")
   failed=True
  count+=1
 if failed:
  return 1
 return 0
if __name__=="__main__":
 sys.exit(main())