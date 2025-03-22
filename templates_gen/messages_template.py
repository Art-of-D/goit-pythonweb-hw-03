from jinja2 import Environment, FileSystemLoader
import json

def generate_html(dir):
  try:

    template_dir = dir.joinpath("templates_gen", "templates")
    storage_dir = dir.joinpath("storage","data.json")
    file_to_write = dir.joinpath("pages", "messages_history.html")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("message_history.html")

    with open(storage_dir, "r", encoding='utf-8') as fh:
      data = json.load(fh)
      data_list = list(data.values())

    output = template.render(data=data_list)
    
    with open(file_to_write, "w", encoding='utf-8') as fh:
      fh.write(output)
  
  except FileNotFoundError as e:
    print(f"File not found: {e}")
  except json.JSONDecodeError as e:
    print(f"Failed to parse JSON: {e}")
  except Exception as e:
    print(f"An error occurred: {e}")

