import argparse
import collections
import configparser
import hashlib
from math import ceil
import os
import re
import zlib
import sys

argparser = argparse.ArgumentParser(description="Command tracker")

argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
argsubparsers.required = True

def main(argv=sys.argv[1:]):
  args = argparser.parse_args(argv)

  if args.command == "init"        : cmd_init(args)


class GitRepository(object):
  
  worktree = None
  gitdir = None
  conf = None

  def __init__(self, path, force=False):
    self.worktree = path
    self.gitdir = os.path.join(path, ".git")

    if not (force or os.path.isdir(self.gitdir)):
      raise Exception("Não é um repositório Git %s" % path)

    # read configuration file in .git/config
    self.conf = configparser.ConfigParser()
    cf = repo_file(self, "config")

    if cf and os.path.exists(cf):
      self.conf.read([cf])
    elif not force:
      raise Exception("Não foi possível obter o arquivo de configuração")

    if not force:
      vers = int(self.conf.get("core", "repositoryformatversion"))
      if vers != 0:
          raise Exception("Versão do formato que o repositório se encontra não é suportado %s" % vers)

# define path
def repo_path(repo, *path):
  return os.path.join(repo.gitdir, *path)
  
# define file
def repo_file(repo, *path, mkdir=False):
  if repo_dir(repo, *path[:-1], mkdir=mkdir):
    return repo_path(repo, *path)

# define repos directory
def repo_dir(repo, *path, mkdir=False):
  path = repo_path(repo, *path)

  if os.path.exists(path):
    if (os.path.isdir(path)):
      return path
    else:
      raise Exception("Não é um diretório %s" % path)

  if mkdir:
    os.makedirs(path)
    return path
  else:
    return None
  
# new repos
def repo_create(path):
  repo = GitRepository(path, True)

  if os.path.exists(repo.worktree):
    if not os.path.isdir(repo.worktree):
      raise Exception ("%s não é um diretório!" % path)
  else:
    os.makedirs(repo.worktree)

  assert(repo_dir(repo, "branches", mkdir=True))
  assert(repo_dir(repo, "objects", mkdir=True))
  assert(repo_dir(repo, "refs", "tags", mkdir=True))
  assert(repo_dir(repo, "refs", "heads", mkdir=True))

  # .git/description
  with open(repo_file(repo, "description"), "w") as f:
    f.write("Repositório sem nome; edite este arquivo 'descrição' para nomear o repositório..\n")

  # .git/HEAD
  with open(repo_file(repo, "HEAD"), "w") as f:
    f.write("ref: refs/heads/master\n")

  with open(repo_file(repo, "config"), "w") as f:
    config = repo_default_config()
    config.write(f)
    
  print(f'Foi inicializado um novo repositório vazio em: {repo.worktree}')
  return repo
  
  
def repo_default_config():
  ret = configparser.ConfigParser()

  ret.add_section("core")
  ret.set("core", "repositoryformatversion", "0")
  ret.set("core", "filemode", "false")
  ret.set("core", "bare", "false")

  return ret
  
argsp = argsubparsers.add_parser("init", help="Inicializar um novo repositório.")
argsp.add_argument("path",
                   metavar="directory",
                   nargs="?",
                   default=".",
                   help="Onde criar o repositório.")
  

def cmd_init(args):
  repo_create(args.path)
  

if __name__=="__main__":
  main()