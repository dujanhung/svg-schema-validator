from pathlib import Path
from lxml import etree
import cssutils
import sys
import urllib.request
import tempfile
RESTRICTED_TAGS={"defs","use","script","image","text"}
class Validator:
 def __init__(self,schema_source:str):
  self.errors=[]
  self.schema=self.load_schema(schema_source)
 def load_schema(self,schema_source:str):
  try:
   if schema_source.startswith("http://") or schema_source.startswith("https://"):
    with urllib.request.urlopen(schema_source) as response:
     data=response.read()
    tmp=tempfile.NamedTemporaryFile(delete=False,suffix=".xsd")
    tmp.write(data)
    tmp.close()
    schema_path=tmp.name
   else:
    schema_path=schema_source
   tree=etree.parse(schema_path)
   return etree.XMLSchema(tree)
  except Exception as e:
   self.errors.append(f"[SCHEMA LOAD ERROR] {schema_source}: {e}")
   return None
 def clean_file(self,file_path:Path)->None:
  raw_lines=file_path.read_text(encoding="utf-8").splitlines()
  lines=[]
  for line in raw_lines:
   if line.strip():
    lines.append(line)
  file_path.write_text("\n".join(lines)+"\n",encoding="utf-8")
 def parse_svg(self,file_path:Path):
  try:
   parser=etree.XMLParser(remove_blank_text=True)
   return etree.parse(str(file_path),parser)
  except etree.XMLSyntaxError as e:
   self.errors.append(f"[XML ERROR] {file_path}: {e}")
   return None
 def validate_schema(self,tree,file_path:Path)->bool:
  if self.schema is None:
   return False
  if not self.schema.validate(tree):
   for error in self.schema.error_log:
    self.errors.append(f"[SCHEMA ERROR] {file_path}: {error}")
   return False
  return True
 def validate_restricted_tags(self,root,file_path:Path)->bool:
  valid=True
  for element in root.iter():
   tag=etree.QName(element).localname
   if tag in RESTRICTED_TAGS:
    self.errors.append(f"[RESTRICTED] {file_path}: <{tag}>")
    valid=False
  return valid
 def validate_css(self,root,file_path:Path)->bool:
  valid=True
  for style in root.xpath("//*[local-name()='style']"):
   css_text=style.text
   if css_text is None:
    css_text=""
   css_text=css_text.strip()
   if not css_text:
    continue
   if "\n\n" in css_text:
    self.errors.append(f"[CSS EMPTY LINE] {file_path}")
    valid=False
   try:
    cssutils.parseString(css_text)
   except Exception as e:
    self.errors.append(f"[CSS ERROR] {file_path}: {e}")
    valid=False
  return valid
 def validate_svg(self,file_path:Path)->bool:
  self.clean_file(file_path)
  tree=self.parse_svg(file_path)
  if tree is None:
   return False
  root=tree.getroot()
  ok=True
  if not self.validate_schema(tree,file_path):
   ok=False
  if not self.validate_restricted_tags(root,file_path):
   ok=False
  if not self.validate_css(root,file_path):
   ok=False
  return ok
def main():
 if len(sys.argv)<3:
  print("✨ usage")
  print(f"🪜 {sys.argv[0]} <schema.xsd|url> <svg-file-or-directory> [...]")
  return 1
 schema_source=sys.argv[1]
 validator=Validator(schema_source)
 files=[]
 for arg in sys.argv[2:]:
  path=Path(arg)
  if path.is_file() and path.suffix.lower()==".svg":
   files.append(path)
  elif path.is_dir():
   files.extend(path.rglob("*.svg"))
 if not files:
  print("❓ No SVG files found")
  return 1
 failed=False
 for file_path in files:
  if validator.validate_svg(file_path):
   print("🟢")
  else:
   print("🔴")
   failed=True
  for error in validator.errors:
   print(f"🪜 {error}")
  validator.errors=[]
 if failed:
  return 1
 return 0
if __name__=="__main__":
 sys.exit(main())