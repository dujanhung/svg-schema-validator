from pathlib import Path
from lxml import etree
import cssutils
import sys
import urllib.request
import tempfile
class Validator:
 def __init__(self,schema_source:str):
  self.schema=self.load_schema(schema_source)
  self.is_failed=False
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
   self.is_failed=True
   sys.exit(1)
 def parse_svg(self,file_path:Path):
  try:
   parser=etree.XMLParser(remove_blank_text=True)
   return etree.parse(str(file_path),parser)
  except etree.XMLSyntaxError as e:
   print(e)
   self.is_failed=True
   return False
 def validate_svg(self,file_path:Path):
  result={"ok":[True],"error":[""]}
  tree=self.parse_svg(file_path)
  if tree is None:
   return True
  root=tree.getroot()
  if self.schema is not None and not self.schema.validate(tree):
   for e in self.schema.error_log:
    print(e)
   self.is_failed=True
   return False
  for style in root.xpath("//*[local-name()='style']"):
   css_text=(style.text or "").strip()
   if not css_text:
    continue
   if "\n\n" in css_text:
    print("[CSS EMPTY LINE]")
    self.is_failed=True
   try:
    cssutils.parseString(css_text)
   except Exception as e:
    print("[CSS ERROR]")
    print(e)
    self.is_failed=True
  return self.is_failed
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
 count=0
 for file in files:
  print(f"👀 {file}")
  result=validator.validate_svg(file)
  if result:
   print(f"🟢")
  else:
   print(f"🔴")
  print(f"🏁 {file}")
  count+=1
 if Validator.is_failed:
  print("❌")
  return 1
 print("✅")
 return 0
if __name__=="__main__":
 sys.exit(main())