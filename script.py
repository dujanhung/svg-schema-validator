from pathlib import Path
from lxml import etree
import cssutils
import os
import sys
import urllib.request
import tempfile
class Validator:
 def __init__(self):
  self.schema=None
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
   os.exit(1)
 def parse_xml(self,file_path:Path):
  try:
   parser=etree.XMLParser(remove_blank_text=True)
   return etree.parse(str(file_path),parser)
  except etree.XMLSyntaxError as e:
   print(e)
   self.is_failed=True
   return "ERR"
 def validate_xml(self,file_path:Path):
  if self.schema is not None:
   if not self.schema.validate(tree):
    for e in self.schema.error_log:
     print(e)
    self.is_failed=True
    return False
  tree=self.parse_xml(file_path)
  if tree=="ERR":
   return False
  if tree is None:
   return True
  root=tree.getroot()
  self.validate_css(root)
 def validate_css(self,root):
  for style in root.xpath("//*[local-name()='style']"):
   css_text=(style.text or "").strip()
   if not css_text:
    continue
   try:
    cssutils.parseString(css_text)
   except Exception as e:
    print("[CSS ERROR]")
    print(e)
    self.is_failed=True
   if "\n\n" in css_text:
    print("[CSS EMPTY LINE]")
    self.is_failed=True
   return self.is_failed
def main():
 if len(sys.argv)<3:
  print("✨ usage")
  print(f"🪜 {sys.argv[0]} <schema.xsd|url> <file|directory>")
  return 1
 validator=Validator()
 Validator.load_schema(sys.argv[1])
 file=""
 path=Path(sys.argv[2])
 if path.is_file() and path.suffix==".svg":
  file=path
 elif path.is_dir():
  file=path.rglob("*.svg")
 print(f"👀 {file}")
 result=validator.validate_xml(file)
 if result:
  print(f"🟢")
 else:
  print(f"🔴")
 print(f"🏁 {file}")
 if Validator.is_failed:
  print("❌")
  return 1
 else
  print("✅")
  return 0
if __name__=="__main__":
 os.exit(main())