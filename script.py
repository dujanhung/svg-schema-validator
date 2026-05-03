from pathlib import Path
from lxml import etree
import cssutils
import sys
RESTRICTED_TAGS={"defs","use","script","image","text"}
class Validator:
 def __init__(self):
  self.errors=[]
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
  if not self.validate_restricted_tags(root,file_path):
   ok=False
  if not self.validate_css(root,file_path):
   ok=False
  return ok
def main():
 if len(sys.argv)<2:
  print(f"Usage: {sys.argv[0]} <svg-file-or-directory> [...]")
  return 1
 validator=Validator()
 files=[]
 for arg in sys.argv[1:]:
  path=Path(arg)
  if path.is_file() and path.suffix.lower()==".svg":
   files.append(path)
  elif path.is_dir():
   files.extend(path.rglob("*.svg"))
 if not files:
  print("No SVG files found.")
  return 1
 failed=False
 for file_path in files:
  if not validator.validate_svg(file_path):
   failed=True
 for error in validator.errors:
  print(error)
 if failed:
  return 1
 return 0
if __name__=="__main__":
 sys.exit(main())