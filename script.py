from pathlib import Path
from lxml import etree
import cssutils
import os
import sys
import urllib.request
import tempfile
FILE_EXT=["xml","md","svg","musicxml","html"]
class Validator:
 def __init__(self):
  self.schema=None
  self.root=None
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
   etree.XMLSchema(tree)
   return True
  except Exception as e:
   print(e)
   return False
 def parse_xml(self,file_path:Path):
  try:
   parser=etree.XMLParser(remove_blank_text=True)
   return etree.parse(str(file_path),parser)
  except Exception as e:
   print(e)
   return "ERR"
 def validate_xml(self,file_path:Path):
  if not self.validate_schema():
   return False
  tree=self.parse_xml(file_path)
  if tree=="ERR":
   return False
  self.root=tree.getroot()
  return True
 def validate_schema(self):
  if self.schema:
   if not self.schema.validate(tree):
    for e in self.schema.error_log:
     print(e)
    return False
   return True
  print("missing XSD data")
  return False
 def validate_css(self):
  if not self.root:
   return True
  for style in root.xpath("//*[local-name()='style']"):
   css_text=(style.text or "").strip()
   if not css_text:
    continue
   try:
    cssutils.parseString(css_text)
   except Exception as e:
    print("[CSS ERROR]")
    print(e)
    return False
   if "\n\n" in css_text:
    print("[CSS EMPTY LINE]")
    return False
  return True
def main():
 if len(sys.argv)<4:
  print("✨ usage")
  print(f"🪜 {sys.argv[0]} <schema.xsd|url> <target> <ext>")
  return 1
 selected_file_ext=sys.argv[3]
 if not selected_file_ext in FILE_EXT:
  print("✨ available file extensions")
  print(FILE_EXT)
  return 1
 file=""
 path=Path(sys.argv[2])
 if path.is_file():
  file=path
 elif path.is_dir():
  print("✨ file")
  return 1
 validator=Validator()
 if not validator.load_schema(sys.argv[1]):
  return 1
 print(f"👀 {file}")
 result=validator.validate_xml(file)
 if result:
  if selected_file_ext in ["svg","html"]:
   result=validator.validate_css()
 if result:
  print(f"🟢")
  return 0
 else:
  print(f"🔴")
  return 1
if __name__=="__main__":
 os.exit(main())