candidate-placer
================

Python engine to select and place candidates to satisfy most of the team needs.

Idea
----

Sometimes it is quite difficult to make decision how to divide N approved
candidates to M teams based on team's requirements as some teams may be
interested in the same candidate profile.<br/>

The decision meeting with team representatives may be quite emotional, that's
why I decided to write piece of software to calm down the discussion...


Example of usage
----------------
  
We have 5 accepted candidates Alice, Bob, Eve, Ann and Frank.
We want to place above candidates to 4 teams tA, tB, tC, tD according
following requirements (team wishlists):
 * team tA: Alice (p1), Eve (p2), Bob (p3)
 * team tB: Alice (p1), Bob (p2)
 * team tC: Frank (p1), Bob (p2), Ann (p3)
 * team tD: Eve (p1), Alice (p2), Frank (p3)

During the negotiation was decided that Frank has to go to team tD.

The tool configuration for above situation is:
<pre><code>./cplacer.py
  # control parameters
  --save-data=a.srl --list-all -s --solve-cnt 3
  # candidates
  -C 'Alice' -C 'Bob' -C 'Eve' -C 'Ann' -C 'Frank'
  # teams
  -T 'tA~1' -T 'tB~1~Nick"s team nick' -T 'tC~1' -T 'tD~2'
  # decisions
  -D 'tD~Frank'
  # team's requirements / wishlists
  -R 'tA~Alice~1' -R 'tA~Bob~3' -R 'tB~Bob~2' -R 'tB~Alice~1' -R 'tC~Ann~3' \
  -R 'tC~Bob~2' -R 'tD~Eve~1' -R 'tA~Eve~2' -R 'tD~Alice~2' -R 'tD~Frank~3' \
  -R 'tC~Frank~1'</code></pre>


Cplacer.py in action...
<pre><code>$ ./cplacer.py --save-data=a.srl --list-all -s --solve-cnt 3 -C 'Alice' -C 'Bob' -C 'Eve' -C 'Ann' -C 'Frank' -T 'tA~1' -T 'tB~1~Nick"s team nick' -T 'tC~1' -T 'tD~2' -D 'tD~Frank' -R 'tA~Alice~1' -R 'tA~Bob~3' -R 'tB~Bob~2' -R 'tB~Alice~1' -R 'tC~Ann~3' -R 'tC~Bob~2' -R 'tD~Eve~1' -R 'tA~Eve~2' -R 'tD~Alice~2' -R 'tD~Frank~3' -R 'tC~Frank~1'
Teams / Positions summary:
  T #00, name:tA, requirements:['#00', '#01', '#07']
  T #01, name:tB, nick:Nick"s team nick, requirements:['#02', '#03']
  T #02, name:tC, requirements:['#04', '#05', '#10']
  T #03, name:tD, requirements:['#06', '#08', '#09'], decision:#00, candidate:Frank(04)
Candidates summary:
  C #00, name:Alice, nick:?, #requirements:['#00', '#03', '#08'], decision:
  C #01, name:Bob, nick:?, #requirements:['#01', '#02', '#05'], decision:
  C #02, name:Eve, nick:?, #requirements:['#06', '#07'], decision:
  C #03, name:Ann, nick:?, #requirements:['#04'], decision:
  C #04, name:Frank, nick:?, #requirements:['#09', '#10'], decision:#00
Requirements summary:
  R #00, name:?, team:tA, candidate:Alice, priority:1
  R #01, name:?, team:tA, candidate:Bob, priority:3
  R #02, name:?, team:tB, candidate:Bob, priority:2
  R #03, name:?, team:tB, candidate:Alice, priority:1
  R #04, name:?, team:tC, candidate:Ann, priority:3
  R #05, name:?, team:tC, candidate:Bob, priority:2
  R #06, name:?, team:tD, candidate:Eve, priority:1
  R #07, name:?, team:tA, candidate:Eve, priority:2
  R #08, name:?, team:tD, candidate:Alice, priority:2
  R #09, name:?, team:tD, candidate:Frank, priority:3
  R #10, name:?, team:tC, candidate:Frank, priority:1
Decisions summary:
  D #00, name:?, team:tD, candidate:Frank
Solver part started:
  25 different placements found
  25/25 placement completed
  25 placements evaluated
Solver found best 3 result[s] (starting from best one):
  Teams/Positions Solution #1 Summary: (dissapointment:394.0)
  T #00, name:tA, requirements:['#00', '#01', '#07'], candidate:Eve(02)
  T #01, name:tB, nick:Nick"s team nick, requirements:['#02', '#03'], candidate:Alice(00)
  T #02, name:tC, requirements:['#04', '#05', '#10'], candidate:Bob(01)
  T #03, name:tD, requirements:['#06', '#08', '#09'], decision:#00, candidate:Frank(04)

  Teams/Positions Solution #2 Summary: (dissapointment:493.0)
  T #00, name:tA, requirements:['#00', '#01', '#07'], candidate:Eve(02)
  T #01, name:tB, nick:Nick"s team nick, requirements:['#02', '#03'], candidate:Alice(00)
  T #02, name:tC, requirements:['#04', '#05', '#10'], candidate:Ann(03)
  T #03, name:tD, requirements:['#06', '#08', '#09'], decision:#00, candidate:Frank(04)

  Teams/Positions Solution #3 Summary: (dissapointment:592.0)
  T #00, name:tA, requirements:['#00', '#01', '#07'], candidate:Eve(02)
  T #01, name:tB, nick:Nick"s team nick, requirements:['#02', '#03'], candidate:Bob(01)
  T #02, name:tC, requirements:['#04', '#05', '#10'], candidate:Ann(03)
  T #03, name:tD, requirements:['#06', '#08', '#09'], decision:#00, candidate:Frank(04)
</code></pre>

Command-line interface
----------------------

<pre><code>$ ./cplacer.py -h
Usage: cplacer.py [options]

Options:
  -h, --help            show this help message and exit
  -T ADD_TEAM, --add-team=ADD_TEAM
                        Append new team/position syntax: <team-name>~<team-
                        priority>[~<team-nick>]
  -C ADD_CANDIDATE, --add-candidate=ADD_CANDIDATE
                        Append new candidate syntax: <cand-name>[~<cand-nick>]
  -R ADD_REQUIREMENT, --add-requirement=ADD_REQUIREMENT
                        Append new team-candidate requirement: <team-name
                        >~<cand-name>~<priority>
  -D ADD_DECISION, --add-decision=ADD_DECISION
                        Append new team-candidate decision: <team-name>~<cand-
                        name>
  --load-data=CFN       Load serialized configuration & solver data (def:
                        none)
  --save-data=CFN       Save serialized configuration & solver data (def:
                        none)
  --list-teams          List all defined teams (def: False)
  --list-candidates     List all defined candidates (def: False)
  --list-requirements   List all defined requirements (def: False)
  --list-decisions      List all defined decisions (def: False)
  -L, --list-all        List all defined data (def: False)
  -s                    Find best candidates placement among teams (def:
                        False)
  --solve-cnt=N         To search for N best candidates placements among teams
                        (def: 1)
  --help-long           Long help
  -v, --verbose         List all test plan/case/run attributes
</code></pre>


TO-DO list:
----------

 * fix bugs
 * enhancements (if requested)
 * pylint fixes
 * test suite
 * GUI?

Requirements
------------

python 2.5+

Files
-----

cplacer.py                main python engine

License
-------

GPL v2
http://www.gnu.org/licenses/gpl-2.0.html


.eof
