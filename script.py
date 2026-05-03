from pathlib import Path
from lxml import etree
import cssutils
import sys
RESTRICTED_TAGS={"defs","use","script","image","text"}
def clean_file(file_path:Path)->None:
 raw_lines=file_path.read_text(encoding="utf-8").splitlines()
 lines=[]
 for line in raw_lines:
  if line.strip():
   lines.append(line)
 file_path.write_text("\n".join(lines)+"\n",encoding="utf-8")
def parse_svg(file_path:Path):
 try:
  parser=etree.XMLParser(remove_blank_text=True)
  return etree.parse(str(file_path),parser)
 except etree.XMLSyntaxError as e:
  print(f"[XML ERROR] {file_path}: {e}")
  return None
def validate_restricted_tags(root,file_path:Path)->bool:
 valid=True
 for element in root.iter():
  tag=etree.QName(element).localname
  if tag in RESTRICTED_TAGS:
   print(f"[RESTRICTED] {file_path}: <{tag}>")
   valid=False
 return valid
def validate_css(root,file_path:Path)->bool:
 valid=True
 for style in root.xpath("//*[local-name()='style']"):
  css_text=style.text
  if css_text is None:
   css_text=""
  css_text=css_text.strip()
  if not css_text:
   continue
  if "\n\n" in css_text:
   print(f"[CSS EMPTY LINE] {file_path}")
   valid=False
  try:
   cssutils.parseString(css_text)
  except Exception as e:
   print(f"[CSS ERROR] {file_path}: {e}")
   valid=False
 return valid
def validate_svg(file_path:Path)->bool:
 print(f"Checking {file_path}")
 clean_file(file_path)
 tree=parse_svg(file_path)
 if tree is None:
  return False
 root=tree.getroot()
 ok=True
 ok&=validate_restricted_tags(root,file_path)
 ok&=validate_css(root,file_path)
 return ok
def main():
 files=list(Path(".").rglob("*.svg"))
 if not files:
  print("No SVG files found.")
  return 0
 failed=False
 for file_path in files:
  if not validate_svg(file_path):
   failed=True
 if failed:
  return 1
 return 0
if __name__=="__main__":
 sys.exit(main())