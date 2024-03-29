import os
from pathlib import Path
from SnippetPattern import snippet_pattern,snippets

work_path = os.path.join(Path(__file__).parent, 'CodePattern')

def main():
    for snippet in snippets:
        path = os.path.join(work_path,snippet['description'])
        # 必须 Unicode ，这里用 uft-8
        with open(path + '.Snippet','w',encoding="utf-8") as file:
            file.write(snippet_pattern.format(**snippet))

if __name__=='__main__':
    main()