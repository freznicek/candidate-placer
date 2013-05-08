#!/usr/bin/env python

'''
Candidate placer (cplacer)

Tool for placing candidates according given requirements / decisions to defined teams/positions

Situation example:
  We have 5 accepted candidates Alice, Bob, Eve, Ann and Frank.
  We want to place above candidates to 4 teams tA, tB, tC, tD according following requirements (team wishlists):
    team tA: Alice (p1), Eve (p2), Bob (p3)
    team tB: Alice (p1), Bob (p2)
    team tC: Frank (p1), Bob (p2), Ann (p3)
    team tD: Eve (p1), Alice (p2), Frank (p3)
  
  During the negotiation was decided that Frank has to go to team tD.
  
  The tool configuration for above situation is:
    ./cplacer.py
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
      -R 'tC~Frank~1'
'''
import sys
import pickle
import optparse

# ---------------------------------------------------------------------------
# classes
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
class Core:
  
  def __init__(self):
    self.reset();
  
  def reset(self):
    self.id = None;
    self.team = None;
    self.candidate = None;
    self.name = None;

  def _str_reqs(self, in_item):
    v = getattr(self, in_item, -1);
    
    if (type(v) == type( [] )):
      int_list = [ ];
      # list
      for i in v:
        int_list.append('#%02d' % i.id);
    else:
      int_list = '';
      if(v != None):
        int_list = '#%02d' % v.id;
    
    return(int_list);
  
  def _strtuple(self):
    n = '?';
    if (self.name != None):
      n = str(self.name);
    c = '?';
    if (self.candidate != None):
      c = str(self.candidate.name);
    t = '?';
    if (self.team != None):
      t = str(self.team.name)
    return(n, c, t);
  
  def __str__(self):
    n, c, t = self._strtuple();
    return("c #%02d, name:%s, team:%s, candidate:%s" % (self.id, n, t, c));

# ---------------------------------------------------------------------------
class Decision(Core):
  
  def __init__(self, in_initstr = None):
    self.reset();
    if (in_initstr != None):
      self.init_from_string(in_initstr);
  
  def init_from_string(self, in_str):
    self.team = in_str.split('~')[0];
    self.candidate = in_str.split('~')[1];

  def __str__(self):
    n, c, t = self._strtuple();
    return("D #%02d, name:%s, team:%s, candidate:%s" % (self.id, n, t, c));

# ---------------------------------------------------------------------------
class Requirement(Core):
  
  def __init__(self, in_initstr = None):
    Core.reset(self);
    self.reset();
    if (in_initstr != None):
      self.init_from_string(in_initstr);
  
  def init_from_string(self, in_str):
    self.team = in_str.split('~')[0];
    self.candidate = in_str.split('~')[1];
    self.priority = int(in_str.split('~')[2]);
  
  def reset(self):
    self.priority = None;

  def __str__(self):
    n, c, t = self._strtuple();
    p = '?';
    if (self.priority != None):
      p = str(self.priority);
    
    return("R #%02d, name:%s, team:%s, candidate:%s, priority:%s" % (self.id, n, t, c, p));


# ---------------------------------------------------------------------------
class Candidate(Core):
  
  def __init__(self, in_initstr = None):
    Core.reset(self);
    self.reset();
    if (in_initstr != None):
      self.init_from_string(in_initstr);
  
  def init_from_string(self, in_str):
    self.name = in_str.split('~')[0];
    if (len(in_str.split('~'))>1):
      self.nick = in_str.split('~')[1];
  
  def reset(self):
    self.nick = None;
    self.decision = None;
    self.requirements = [ ];

  def __eq__(self, in_o):
    if (type(self) == type(in_o)):
      return(self.name == in_o.name);
    else:
      return(False);
  
  def __str__(self):
    n, c, t = self._strtuple();
    ni = '?';
    if (self.nick != None):
      ni = str(self.nick);
    return("C #%02d, name:%s, nick:%s, #requirements:%s, decision:%s" % (self.id, n, ni, self._str_reqs('requirements'), self._str_reqs('decision')));


# ---------------------------------------------------------------------------
class Team(Core):
  
  def __init__(self, in_initstr = None):
    Core.reset(self);
    self.reset();
    if (in_initstr != None):
      self.init_from_string(in_initstr);
  
  def init_from_string(self, in_str):
    self.name = in_str.split('~')[0];
    self.priority = int(in_str.split('~')[1]);
    if (len(in_str.split('~'))>2):
      self.nick = in_str.split('~')[2];
  
  def reset(self):
    self.nick = None;
    self.priority = None;
    self.decision = None;
    self.requirements = [ ];
    self.candidate = None;

  def set_decision(self, in_decision):
    if (self.decision == None):
      self.candidate = in_decision.candidate;
      self.decision = in_decision;
    else:
      raise Exception("Team.set_decision() failed while another decision in place already!");
  
  def reset_decision(self):
    self.decision = None;
  
  def select_candidate(self, in_cand):
    if (self.decision == None):
      self.candidate = in_cand;
    else:
      raise Exception("Team.select_candidate() failed while decision in place already!");
  
  def deselect_candidate (self, in_cand = None):
    if (self.decision == None):
      self.candidate = None;
    else:
      raise Exception("Team.deselect_candidate() failed while decision in place already!");

  def get_dissapointment(self):
    team_koef = 1.0 * (100 - self.priority);
    cand_koef = 10.0; # candidate not selected
    if (self.candidate != None):
      cand_koef = 9.0; # candidate selected but not in the requirements
      for i_r in self.requirements:
        if (i_r.candidate == self.candidate):
          cand_koef = (i_r.priority - 1.0);
          break;
    
    # find whether currently selected candidate is on the priority list, if so (prio - 1) else 9.0/10.0
    ###print "get_dissapointment(): %s (%s)" % ( str(team_koef * cand_koef), self.candidate);
    return(team_koef * cand_koef);
  
  def get_match(self):
    return(self.get_dissapointment());
  
  def __str__(self):
    int_str = "T #%02d, name:%s" % (self.id, self.name);
    if (self.nick != None):
      int_str += ", nick:%s" % self.nick;
    if (self.requirements != None):
      int_str += ", requirements:%s" % self._str_reqs('requirements');
    if (self.decision != None):
      int_str += ", decision:%s" % self._str_reqs('decision');
    if (self.candidate != None):
      int_str += ", candidate:%s(%02d)" % (self.candidate.name, self.candidate.id);
    
    return(int_str);

# ---------------------------------------------------------------------------
class Choice:
  def __init__(self, in_loc = None):
    self.reset();
    if (in_loc != None):
      self.init(in_loc);
  
  def reset(self):
    self.lindx = [ ];
    self.loc = None;
    self.lindx_start = None;
    self.iteration = None;
    self.lchoice = None;
  
  def init(self, in_loc):
    self.loc = in_loc;
    self.lindx = [0] * len(self.loc);
    self.lindx_start = [0] * len(self.loc);
    ###print "Choice.init():" + str(self.loc) + str(self.lindx) + str(self.lindx_start)
    self.lchoice = None;
  
  def _next_indx(self):
    ret_val = True;
    lindx = self.lindx[:];
    
    if self.iteration == None:
      # first query
      self.iteration = 0;
    else:
      for indx in xrange(len(lindx)-1, -1, -1):
        # browse 'digits' from right to left
        lindx[indx] = (lindx[indx] + 1) % len(self.loc[indx]);
        if (lindx[indx] != 0):
          # 'digit' incremented and did not turned into higher one
          break;
      
      self.iteration += 1;
      if (lindx == self.lindx_start):
        # next step is starting point - stop
        ret_val = False;
      else:
        # next step is available
        self.lindx = lindx;
    
    return(ret_val);

  def _indx2choice(self):
    int_list = [ ];
    for i_i in xrange(len(self.lindx)):
      int_list.append(self.loc[i_i][self.lindx[i_i]]);
    self.lchoice = int_list;
    return(int_list);
  
  def _choice_check(self):
    int_res = True;
    if (self.lchoice != None):
      for i in self.lchoice:
        if( (i != None) and (self.lchoice.count(i)>1) ):
          int_res = False;
          break;
    else:
      int_res = False;
    return(int_res);
    
  def next(self):
    ret_val = None;
    while (True):
      if (self._next_indx()):
        self._indx2choice();
        if (self._choice_check()):
          return(self.lchoice);
        else:
          continue;
      else:
        break;
    return(ret_val);


# ---------------------------------------------------------------------------
class Solver(object):
  def __init__(self, in_data, in_best_option_cnt=1):
    self.reset(in_data, in_best_option_cnt);
    
  def reset(self, in_data = None, in_best_option_cnt = None):
    self.data = None;
    if (in_data != None):
      self.data = in_data;
    # object carying the current choice
    self.choice = None;
    # list of choices
    self.loc = [ ];
    # dict - best choices
    self.dbc = { };
    self.dbc_maxlen = 0;
    if (in_best_option_cnt != None):
      self.dbc_maxlen = in_best_option_cnt;
  
  def get_combination_cnt(self):
    self.init();
    int_cnt = 0;
    while (self.choice.next()):
      int_cnt += 1;
    return(int_cnt);

  def init(self):
    # transform the list of teams into self.loc
    for i_t in self.data['teams']:
      # browse teams
      int_list = [ ];
      if (i_t.decision != None):
        # decision pending - one case
        int_list.append(i_t.decision.candidate.id);
      else:
        # team might not get anyone
        int_list.append(None);
        for i_r in i_t.requirements:
          # browse team's requirements
          int_list.append(i_r.candidate.id);
      # append new options for current team
      self.loc.append(int_list);
    
    self.choice = Choice(self.loc);

  
  def _append_choice_data(self, in_dissapointment, in_choice):
    ###print in_dissapointment, in_choice, self.dbc;
    max_key = -1;
    if (len(self.dbc.keys()) > 0):
      max_key = max(self.dbc.keys());
    if( (len(self.dbc.keys()) == 0) or (in_dissapointment < max_key) ):
      # we found better solution - need to remember
      if (len(self.dbc.keys()) >= self.dbc_maxlen):
        # delete worst result
        del self.dbc[max_key];
      self.dbc[in_dissapointment] = in_choice;
  
  def next(self):
    # get current choice
    ch = self.choice.next();
    if(ch != None):
      d = 0.0;
      for indx in xrange(len(ch)):
        # browse teams
        if (self.data['teams'][indx].decision == None):
          # candidate selection
          self.data['teams'][indx].deselect_candidate();
          if (ch[indx] != None ):
            self.data['teams'][indx].select_candidate(self.data['candidates'][ch[indx]]);
        d += self.data['teams'][indx].get_dissapointment();
      
      # remember choice and result
      self._append_choice_data(d, ch);
      
      return(True);
    else:
      return(False);
  
  def get_results(self):
    return(self.dbc);


# common methods
# ---------------------------------------------------------------------------

def update_ids(in_list):
  for i in xrange(len(in_list)):
    in_list[i].id = i;

def find_object(in_list, in_name):
  int_obj = None;
  for i in in_list:
    if (i.name == in_name):
      int_obj = i;
      break;
    if ( ('nick' in dir(i)) and (i.nick == in_name) ):
      int_obj = i;
      break;
    
  return(int_obj);


# main() definition
# ---------------------------------------------------------------------------
def main(in_opts):
  
  # data storage
  # -------------------------------------------------------------------------
  data = { };
  data['teams'] = [ ];
  data['candidates'] = [ ];
  data['requirements'] = [ ];
  data['decisions'] = [ ];
  
  # load configuration
  if (in_opts['load_data'] != None):
    fh = open(in_opts['load_data'], 'r');
    data = pickle.load(fh);
    fh.close();
  else:
    # fill in the teams
    indx = 0
    for i_t in in_opts['add_team']:
      data['teams'].append(Team(i_t));
    update_ids(data['teams']);
    # fill in the candidates
    for i_c in in_opts['add_candidate']:
      data['candidates'].append(Candidate(i_c));
    update_ids(data['candidates']);
    # fill in the requirements
    for i_r in in_opts['add_requirement']:
      data['requirements'].append(Requirement(i_r));
    update_ids(data['requirements']);
    # fill in the decisions
    for i_d in in_opts['add_decision']:
      data['decisions'].append(Decision(i_d));
    update_ids(data['decisions']);
  
    # link decisions to objects
    for i_d in data['decisions']:
      t = find_object(data['teams'], i_d.team);
      c = find_object(data['candidates'], i_d.candidate);
      if ((None == c) or (t == None)):
        raise Exception("Decision %s is invalid" % i_d);
      i_d.team = t;
      i_d.candidate = c;
      t.set_decision(i_d);
      c.decision = i_d;
      
    # link requirements to objects
    for i_r in data['requirements']:
      t = find_object(data['teams'], i_r.team);
      c = find_object(data['candidates'], i_r.candidate);
      if ((None == c) or (t == None)):
        raise Exception("Requirement %s is invalid" % i_r);
      i_r.team = t;
      i_r.candidate = c;
      t.requirements.append(i_r);
      c.requirements.append(i_r);
  
  # object listing
  # -------------------------------------------------------------------------
  if( (in_opts['list_teams']) or (in_opts['list_all']) ):
    print "Teams / Positions summary:"
    for i_t in data['teams']:
      print "  %s" % i_t;
  if( (in_opts['list_candidates']) or (in_opts['list_all']) ):
    print "Candidates summary:"
    for i_c in data['candidates']:
      print "  %s" % i_c;
  if( (in_opts['list_requirements']) or (in_opts['list_all']) ):
    print "Requirements summary:"
    for i_r in data['requirements']:
      print "  %s" % i_r;
  if( (in_opts['list_decisions']) or (in_opts['list_all']) ):
    print "Decisions summary:"
    if (len(data['decisions'])>0):
      for i_d in data['decisions']:
        print "  %s" % i_d;
    else:
      print "  <none>";
  
  # solver part
  # -------------------------------------------------------------------------
  results = None;
  if (in_opts['solve'] == True):
    
    print "Solver part started:"
    solver = Solver(in_data = data, in_best_option_cnt = in_opts['solve_cnt']);
    
    # get number of variations
    loop_cnt = solver.get_combination_cnt();
    print "  %d different placements found" % loop_cnt;
    
    # find the N best choices
    solver.reset(in_data = data, in_best_option_cnt = in_opts['solve_cnt']);
    solver.init();
    i_loop = 0
    while (solver.next()):
      print "  %d/%d placement completed\r" % (i_loop+1, loop_cnt),
      i_loop += 1;
    print "\n  %d placements evaluated" % i_loop;
    
    # get results
    results = solver.get_results();
    # store results (allow to be serialized)
    data['results'] = results;
    ###print results, results.keys();
  else:
    if ('results' in data):
      results = data['results'];
  
  # save configuration/data
  # -------------------------------------------------------------------------
  if (in_opts['save_data'] != None):
    fh = open(in_opts['save_data'], 'w')
    pickle.dump(data, fh);
    fh.close();
  
  # result presentation
  # -------------------------------------------------------------------------
  if (len(results.keys())>0):
    print "Solver found best %d result[s] (starting from best one):" % len(results.keys());
    indx=1
    r_keys = results.keys()[:];
    r_keys.sort();
    for i_d in r_keys:
      print "  Teams/Positions Solution #%d Summary: (dissapointment:%.1f)" % (indx, i_d);
      for indx2 in xrange(len(data['teams'])):
        if (data['teams'][indx2].decision == None):
          data['teams'][indx2].deselect_candidate();
          if (results[i_d][indx2] != None ):
            data['teams'][indx2].select_candidate(data['candidates'][results[i_d][indx2]]);
        print "  %s" % data['teams'][indx2];
      print "";
      indx += 1;
  else:
    print "An error occurred, no solution found";
    
    ###print in_opts;
    ###print data;
    ###print results;



# main() call
# ---------------------------------------------------------------------------
if __name__ == "__main__":

  # parameters definition and parsing
  # -------------------------------------------------------------------------
  usage_msg = "usage: %prog [options]";
  op = optparse.OptionParser(usage=usage_msg);

  # define parameters
  # -------------------------------------------------------------------------
  op.add_option("-T", "--add-team", dest="add_team",
                action="append", default=[],
                help="Append new team/position syntax: <team-name>~<team-priority>[~<team-nick>]");
  op.add_option("-C", "--add-candidate", dest="add_candidate",
                action="append", default=[],
                help="Append new candidate syntax: <cand-name>[~<cand-nick>]");
  op.add_option("-R", "--add-requirement", dest="add_requirement",
                action="append", default=[],
                help="Append new team-candidate requirement: <team-name>~<cand-name>~<priority>");
  op.add_option("-D", "--add-decision", dest="add_decision",
                action="append", default=[],
                help="Append new team-candidate decision: <team-name>~<cand-name>");
  
  op.add_option("--load-data", dest="load_data", type="string",
                action="store", default=None,
                help="Load serialized configuration & solver data (def: %default)", metavar="CFN");
  op.add_option("--save-data", dest="save_data", type="string",
                action="store", default=None,
                help="Save serialized configuration & solver data (def: %default)", metavar="CFN");
  
  op.add_option("--list-teams", dest="list_teams",
                action="store_true", default=False,
                help="List all defined teams (def: %default)");
  op.add_option("--list-candidates", dest="list_candidates",
                action="store_true", default=False,
                help="List all defined candidates (def: %default)");
  op.add_option("--list-requirements", dest="list_requirements",
                action="store_true", default=False,
                help="List all defined requirements (def: %default)");
  op.add_option("--list-decisions", dest="list_decisions",
                action="store_true", default=False,
                help="List all defined decisions (def: %default)");
  op.add_option("-L", "--list-all", dest="list_all",
                action="store_true", default=False,
                help="List all defined data (def: %default)");
  
  op.add_option("-s", dest="solve",
                action="store_true", default=False,
                help="Find best candidates placement among teams (def: %default)");
  op.add_option("--solve-cnt", dest="solve_cnt", type="int",
                action="store", default=1, metavar="N",
                help="To search for N best candidates placements among teams (def: %default)");
  
  op.add_option("--help-long", dest="help_long",
                action="store_true", default=False,
                help="Long help");
  
  op.add_option("-v", "--verbose", dest="verbose",
                action="store_true", default=False,
                help="List all test plan/case/run attributes");
  
  (opts, args) = op.parse_args();
  
  if (opts.help_long):
    print __doc__;
    op.print_help();
    sys.exit(0);
  
  int_opts = { };
  int_opts = eval('%s' % opts);
  
  main(int_opts);


# ---------------------------------------------------------------------------
# eof
# ---------------------------------------------------------------------------
