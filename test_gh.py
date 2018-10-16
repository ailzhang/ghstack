import textwrap
import doctest
import expecttest
import unittest
import subprocess
import warnings
import os

import gh


def dump_github_state(github):
    r = github.graphql("""
      query {
        repository(name: "pytorch", owner: "pytorch") {
          pullRequests {
            nodes {
              number
              baseRefName
              headRefName
              title
              body
            }
          }
        }
      }
    """)
    print(r)


def create_pr(github):
    r = github.graphql("""
      mutation {
        createPullRequest(input: {
            baseRefName: "master",
            headRefName: "blah",
            title: "New PR",
            body: "What a nice PR this is",
            ownerId: 1000,
          }) {
          pullRequest {
            number
          }
        }
      }
    """)
    print(r)


class TestGh(expecttest.TestCase):
    # Starting up node takes 0.7s.  Don't do it every time.
    @classmethod
    def setUpClass(cls):
        port = 49152
        # Find an open port to run our tests on
        while True:
            cls.proc = subprocess.Popen(['node', 'github-fake/src/index.js', str(port)], stdout=subprocess.PIPE, stderr=open(os.devnull, 'w'))
            r = cls.proc.stdout.readline()
            if not r.strip():
                cls.proc.terminate()
                cls.proc.wait()
                port +=1
                print("Retrying with port {}".format(port))
                continue
            break
        cls.github = gh.Endpoint("http://localhost:{}".format(port))

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        cls.proc.wait()

    def setUp(self):
        self.github.graphql("""
          mutation {
            resetGitHub(input: {})
          }
        """)

    def test_basic(self):
        create_pr(self.github)
        create_pr(self.github)
        dump_github_state(self.github)
        print("shufflin")


#   def load_tests(loader, tests, ignore):
#       tests.addTests(doctest.DocTestSuite(gh))
#       return tests


if __name__ == '__main__':
    unittest.main()
