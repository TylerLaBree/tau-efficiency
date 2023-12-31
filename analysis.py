### A series of tools for analyzing tau neutrino events using DUNE software(dunesw)-wrapped GENIE ###

import ROOT
import dunestyle.matplotlib as dunestyle
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from particles import *
from particle import Particle

mpl.rcParams["mathtext.fontset"] = "cm"
mpl.rcParams["font.family"] = "serif"
mpl.rcParams["font.serif"] = "Computer Modern"

dune_colors = ['#D55E00', '#56B4E9', '#E69F00']
okabe_ito_colors = ['#000000', '#D55E00', '#56B4E9', '#E69F00', '#009E73', '#CC79A7', '#0072B2', '#F0E442']

### --Event Attributes------------------------------------------------------ ###

def get_nuance_code(datatype, event):
  # Event attribute
  if datatype == "gst":
    return event.nuance_code 
  elif datatype == "dunesw":
    mc_neutrino = event.product()[0].GetNeutrino()
    return mc_neutrino.InteractionType() - 1000
  else:
    print("oops")
    return None

def get_neut_code(datatype, event):
  # Event attribute
  if datatype == "gst":
    return event.neut_code
  else:
    print("oops")
    return None

def get_scattering_code(datatype, event):
  # Event attribute
  if datatype == "dunesw":
    mc_neutrino = event.product()[0].GetNeutrino()
    return mc_neutrino.Mode()
  else:
    print("oops")
    return None

def get_number_particles(datatype, event):
  # Event attribute
  if datatype == "gtrac":
    return event.StdHepN
  elif datatype == "dunesw":
    return event.product()[0].NParticles()
  else:
    print("oops")
    return None


### --Particle Attributes--------------------------------------------------- ###

def get_is_particle_descendant(criteria_function, datatype, particle, acc=False):
  # Particle attribute
  if acc: return True
  (event, i) = particle
  if i == None: return False
  return get_is_particle_descendant(criteria_function, datatype, get_mother(datatype, particle), acc or criteria_function(datatype, particle))

def get_is_final_state(datatype, particle):
  # Particle attribute
  # StatusCode == 1 means stable final state
  # StatusCode == 15 means final state nuclear remnant
  return get_status_code(datatype, particle) in [1, 15]

def get_status_code(datatype, particle):
  # Particle attribute
  (event, i) = particle
  if datatype == "dunesw":
    mc_particle = event.product()[0].GetParticle(i)
    return mc_particle.StatusCode()
  else:
    print("oops")
    return None

def get_name(datatype, particle):
  # Particle attribute
  return get_particle_name(get_pdg_code(datatype, particle))

def get_index(datatype, particle):
  # Particle attribute
  (event, i) = particle
  return i

def get_mother_index(datatype, particle):
  # Particle attribute
  (event, i) = particle
  if datatype == "gtrac":
    index = event.StdHepFm[i]
  elif datatype == "dunesw":
    mc_particle = event.product()[0].GetParticle(i)
    index = mc_particle.Mother()
  else:
    print("oops")
    return None
  if index == -1:
    return None
  return index

def get_mother(datatype, particle):
  # Particle attribute
  (event, i) = particle
  if i is None:
    return (event, None)
  return (event, get_mother_index(datatype, particle))

def get_four_momentum(datatype, particle):
  # Particle attribute
  (event, i) = particle
  if datatype == "gtrac":
    return [event.StdHepP4[4*i+j] for j in range(4)]
  elif datatype == "dunesw":
    mc_particle = event.product()[0].GetParticle(i)
    return [mc_particle.Momentum()[j] for j in range(4)]
  else:
    print("oops")
    return None

def get_pdg_code(datatype, particle):
  # Particle attribute
  (event, i) = particle
  if i is None:
    return None
  if datatype == "gtrac":
    return event.StdHepPdg[i] 
  elif datatype == "dunesw":
    mc_particle = event.product()[0].GetParticle(i)
    return mc_particle.PdgCode()
  else:
    print("oops")
    return None

def get_first_daughter_index(datatype, particle):
  # Particle attribute
  (event, i) = particle
  if datatype == "gtrac":
    index = event.StdHepFd[i]
  elif datatype == "dunesw":
    mc_particle = event.product()[0].GetParticle(i)
    index = mc_particle.FirstDaughter()
  else:
    print("oops")
    return None
  if index == -1:
    return None
  else:
    return index

def get_last_daughter_index(datatype, particle):
  # Particle attribute
  (event, i) = particle
  if datatype == "gtrac":
    index = event.StdHepLd[i]
  elif datatype == "dunesw":
    mc_particle = event.product()[0].GetParticle(i)
    index = mc_particle.LastDaughter()
  else:
    print("oops")
    return None
  if index == -1:
    return None
  else:
    return index

def get_daughters(datatype, particle):
  # Particle attribute
  (event, i) = particle
  acc = []
  for j in range(get_number_particles(datatype, event)):
    if get_mother_index(datatype, (event, j)) == i:
      acc.append(j)
  return acc

def get_number_daughters(datatype, particle):
  # Particle attribute
  return len(get_daughters(datatype, particle))

def get_is_lepton_decay_product(datatype, particle): return get_is_leading_lepton(datatype, get_mother(datatype, particle))

def get_is_interaction_product(datatype, particle): return get_is_initial_atom(datatype, get_mother(datatype, particle))

def get_is_lepton_decay_topology(datatype, particle): 
  return get_is_final_state(datatype, particle) \
         and get_is_particle_descendant(get_is_leading_lepton, datatype, particle)

def get_is_interaction_topology(datatype, particle): 
  return get_is_final_state(datatype, particle) \
         and get_is_particle_descendant(get_is_initial_atom, datatype, particle)

def get_is_charged_hadron(datatype, particle):
  return get_name(datatype, particle) in ["pi+", "pi-", "K+", "K-"]

def get_is_signal_charged_hadron(datatype, particle):
  return get_name(datatype, particle) in ["pi+", "pi-", "K+", "K-"] \
         and get_is_lepton_decay_topology(datatype, particle)

def get_is_background_charged_hadron(datatype, particle):
  return get_name(datatype, particle) in ["pi+", "pi-", "K+", "K-"] \
         and get_is_interaction_topology(datatype, particle)


### --Math------------------------------------------------------------------ ###

def get_particle_name(pdg_code):
  try:
    return Particle.from_pdgid(pdg_code).name
  except:
    return pdg_code

def get_momentum(four_momentum):
  return [four_momentum[0], four_momentum[1], four_momentum[2]]

def get_energy(four_momentum):
  return four_momentum[3]

def get_normalized_vector(v):
  return [elt/magnitude(v) for elt in v]

def get_transverse_momentum(momentum, beamline_direction):
  beamline_direction = get_normalized_vector(beamline_direction)
  return magnitude(get_cross_product(momentum, beamline_direction))

def magnitude(v):
  if len(v) != 3:
    print("ERROR: vector not the right length")
    return None
  return np.sqrt(sum(i**2 for i in v))

def dot_product(u, v):
  if len(u) != 3 or len(v) != 3:
    print("ERROR: vector not the right length")
    return 0
  return sum(i[0] * i[1] for i in zip(u, v))

def get_cross_product(u, v):
  return [get_determinant_2d([u[i], u[j]], [v[i], v[j]]) for (i,j) in [(1,2), (0,2), (0,1)]]

def get_determinant_2d(a, b):
  return a[0]*b[1] - a[1]*b[0]

def angle(u, v):
  return np.arccos(dot_product(u, v)/magnitude(u)/magnitude(v))

def get_lepton_energy_loss(e_nu, e_ll):
  # Lab neutrino energy transfer (ν)
  return e_nu - e_ll

def get_scattering_angle(p_nu, p_ll):
  # Lab scattering angle (θ)
  return angle(p_nu, p_ll)

def get_w_sq(m_t, nu, q_sq):
  # Invariant hadronic mass squared (W^2)
  return m_t**2 + 2*m_t*nu - q_sq

def get_x(q_sq, m_t, nu):
  # Bjorken scaling variable, Feynman scaling variable (x)
  return q_sq**2 / (2*m_t*nu)

def get_y(nu, e_nu):
  # Relative energy transfer, inelasticity (y)
  return nu / e_nu

def get_sqrt_s(m_t, q_sq, x, y):
  # Center of mass scattering energy (√s)
  return m_t**2 + q_sq/(x*y)

def get_interaction_type(interaction_code, category):
  if interaction_code == 0:
    return None
  if category == "nuance":
    code_to_name = nuance_code_to_name
  elif category == "neut":
    code_to_name = neut_code_to_name
  elif category == "scattering":
    code_to_name = scattering_code_to_name
  else:
    print("oops")
    return None
  try:
    return code_to_name[interaction_code]
  except:
    return interaction_code

def get_type_fallback(main_type, backup_type):
  if main_type == None:
    return backup_type
  else:
    return main_type

def get_simple_interaction_type(interaction_type):
  possible_names = ["DIS", "RES", "QE", "MEC","None"]
  for possible_name in possible_names:
    if possible_name in interaction_type.upper():
      return possible_name

def get_total_transverse_momentum(momenta, beamline_direction):
  return get_transverse_momentum(sum_vectors(momenta), beamline_direction)

### --Event Loop Logic------------------------------------------------------ ###

def read_header(h):
  """Make the ROOT C++ jit compiler read the specified header."""
  ROOT.gROOT.ProcessLine('#include "%s"' % h)

def provide_get_valid_handle(klass):
  """Make the ROOT C++ jit compiler instantiate the
     Event::getValidHandle member template for template
     parameter klass."""
  ROOT.gROOT.ProcessLine('template gallery::ValidHandle<%(name)s> gallery::Event::getValidHandle<%(name)s>(art::InputTag const&) const;' % {'name' : klass})

def get_event_attribute(attribute_function, datatype, event):
  return attribute_function(datatype, event)

def get_particle_attribute(attribute_function, criteria_function, datatype, event):
  attribute = [attribute_function(datatype, (event, i)) for i in range(get_number_particles(datatype, event)) if criteria_function(datatype, (event, i))]
  return attribute

def get_attributes_gst(attribute_definitions, filename, sample_size=10):
  file = ROOT.TFile.Open(filename,"READ")
  tree = file.Get("gst")
  num_entries = tree.GetEntries()
  count = 0
  attributes = {}
  for attribute_definition in attribute_definitions:
    attributes[attribute_definition[0]] = []
  for event in tree:
    if count >= sample_size: break
    for attribute_definition in attribute_definitions:
      (attribute_name, attribute_function, criteria_function) = attribute_definition
      if criteria_function == None:
        attributes[attribute_name].append(get_event_attribute(attribute_function, "gst", event))
      else:
        attributes[attribute_name].append(get_particle_attribute(attribute_function, criteria_function, "gst", event))
    count += 1
  return attributes

def get_attributes_gtrac(attribute_definitions, filename, sample_size=10):
  file = ROOT.TFile.Open(filename,"READ")
  tree = file.Get("gRooTracker")
  num_entries = tree.GetEntries()
  count = 0
  attributes = {}
  for attribute_definition in attribute_definitions:
    attributes[attribute_definition[0]] = []
  for event in tree:
    if count >= sample_size: break
    for attribute_definition in attribute_definitions:
      (attribute_name, attribute_function, criteria_function) = attribute_definition
      if criteria_function == None:
        attributes[attribute_name].append(get_event_attribute(attribute_function, "gtrac", event))
      else:
        attributes[attribute_name].append(get_particle_attribute(attribute_function, criteria_function, "gtrac", event))
    count += 1
  return attributes

def get_attributes_dunesw(attribute_definitions, filename, sample_size=10):
  mctruths_tag = ROOT.art.InputTag("generator")
  filenames = ROOT.vector(ROOT.string)(1, filename)
  event = ROOT.gallery.Event(filenames)
  get_mctruths = event.getValidHandle[ROOT.vector(ROOT.simb.MCTruth)]
  count = 0
  attributes = {}
  for attribute_definition in attribute_definitions:
    attributes[attribute_definition[0]] = []
  while (not event.atEnd()) :
    mctruths = get_mctruths(mctruths_tag)
    if count >= sample_size or mctruths.empty(): break
    for attribute_definition in attribute_definitions:
      (attribute_name, attribute_function, criteria_function) = attribute_definition
      if criteria_function == None:
        attributes[attribute_name].append(get_event_attribute(attribute_function, "dunesw", mctruths))
      else:
        attributes[attribute_name].append(get_particle_attribute(attribute_function, criteria_function, "dunesw", mctruths))
    count += 1
    event.next()
  return attributes

def dump_particle_list_dunesw(filename, sample_size=10):
  mctruths_tag = ROOT.art.InputTag("generator")
  datatype = "dunesw"
  filenames = ROOT.vector(ROOT.string)(1, filename)
  event = ROOT.gallery.Event(filenames)
  get_mctruths = event.getValidHandle[ROOT.vector(ROOT.simb.MCTruth)]
  count = 0
  while (not event.atEnd()) :
    mctruths = get_mctruths(mctruths_tag)
    if count >= sample_size or mctruths.empty(): break
    print()
    print("~~~~~~~ Event", count, "~~~~~~~")
    for i in range(get_number_particles(datatype, mctruths)):
      particle = (mctruths, i)
      daughters = get_daughters(datatype, particle)
      print(i, get_particle_name(get_pdg_code(datatype, particle)), "kiddos:", daughters)
    count += 1
    event.next()


### --More Math------------------------------------------------------------ ###

def count_elts(my_list):
  elt_counts = {}
  for elt in my_list:
    if elt not in elt_counts :
      elt_counts[elt] = 0
    elt_counts[elt] += 1
  return elt_counts

def get_tau_decay_type(tau_decay_product_set):
  for possible_decay_product_name, possible_decay_product_sets in tau_decay_modes_simple.items():
    if tau_decay_product_set in possible_decay_product_sets:
      return possible_decay_product_name
  return None

def sum_vectors(vs):
  if len(vs) == 0:
    return [0,0,0]
  acc = [0]*len(vs[0])
  for v in vs:
    for i in range(len(v)):
      acc[i] += v[i]
  return acc

def flatten_1d(list_of_lists):
  return [row[0] if len(row)==1 else None for row in list_of_lists]

def flatten(list_of_lists):
  return [item for row in list_of_lists for item in row]

def get_knitted_dictionaries(a, b): # knit two sets of keys and values into one set of keys and value pairs
  value_pairs_dict = {}
  for key in list(set(list(a.keys()) + list(b.keys()))):
    value_pairs_dict[key] = (a[key] if key in a else 0, b[key] if key in b else 0) 
  return value_pairs_dict


### --Graph Types----------------------------------------------------------- ###

def get_bar_graph(counted_set, y_label):
  width = 0.8
  fig, ax = plt.subplots()
  xs = np.arange(len(counted_set.keys()))
  ax.bar(xs, [y for y in list(counted_set.values())], tick_label=[y for y in list(counted_set.keys())])
  #ax.set_xticks(xs + width/2, counted_set.keys())
  ys = np.arange(0,110,10)
  ax.set_yticks(ys, list(map(lambda y : str(int(y))+"%", ys)))
  ax.set_ylabel(y_label)
  dunestyle.Simulation(ax=ax)
  return fig

def get_double_bar_graph(item_pairs, datum_labels, colors, y_label):
  fig, ax = plt.subplots()
  width = 0.3
  xs = np.arange(len(item_pairs.keys()))
  ax.bar(xs, [y for (y, _) in list(item_pairs.values())], color=colors[0], label=datum_labels[0], width=width)
  ax.bar(xs + width, [y for (_, y) in list(item_pairs.values())], color=colors[1], label=datum_labels[1], width=width)
  ax.set_xticks(xs + width/2, item_pairs.keys())
  ys = np.arange(0,110,10)
  ax.set_yticks(ys, list(map(lambda y : str(int(y))+"%", ys)))
  ax.set_ylabel(y_label)
  ax.legend()
  dunestyle.Simulation(ax=ax)
  return fig

def get_one_parameter_histogram(data, datum_labels, edge_colors, x_label, y_label, x_limits, number_bins):
  fig, ax = plt.subplots()
  for (datum, datum_label, edge_color) in zip(data, datum_labels, edge_colors):
    ax.hist(datum, number_bins, x_limits, histtype="step", edgecolor=edge_color, label=datum_label)
  ax.set_xlabel(x_label)
  ax.set_ylabel(y_label)
  ax.legend()
  dunestyle.Simulation(ax=ax)
  return fig

def get_scatter_plot(xs_data, ys_data, datum_labels, colors, x_label, y_label, x_limits, y_limits):
  fig, ax = plt.subplots()
  for (xs, ys, datum_label, color) in zip(xs_data, ys_data, datum_labels, colors):
    ax.scatter(xs, ys, c=color, label=datum_label, marker=".")
  ax.set_xlabel(x_label)
  ax.set_ylabel(y_label)
  ax.set_xlim(x_limits[0], x_limits[1])
  ax.set_ylim(y_limits[0], y_limits[1])
  ax.legend()
  dunestyle.Simulation(ax=ax)
  return fig

def get_profile_histogram(xs_data, ys_data, datum_labels, colors, x_label, y_label, x_limits, y_limits, number_bins):
  fig, ax = plt.subplots()
  for (xs, ys, datum_label, color) in zip(xs_data, ys_data, datum_labels, colors):
    x_bin_width = (x_limits[1] - x_limits[0])/number_bins
    x_bin_centers = np.linspace(x_limits[0] + x_bin_width/2, x_limits[1] + x_bin_width/2, number_bins, endpoint=False)
    x_bin_errors = [x_bin_width/2]*number_bins
    binned_ys = [[y for (x,y) in zip(xs, ys) if x_bin_center - x_bin_width/2 <= x < x_bin_center + x_bin_width/2] for x_bin_center in x_bin_centers]
    y_counts = [len(ys) if len(ys) > 1 else 2 for ys in binned_ys]
    y_sums = [sum(ys) if len(ys) > 1 else 0 for ys in binned_ys]
    y_squared_sums = [sum(map(lambda y: y**2, ys)) if len(ys) > 1 else 0 for ys in binned_ys]
    y_averages = list(map(lambda a, b: a/b, y_sums, y_counts))
    y_squared_averages = list(map(lambda a, b: a/b, y_squared_sums, y_counts))
    y_variances = [y_count/(y_count - 1) * (y_squared_average - y_average**2) for (y_count, y_average, y_squared_average) in zip(y_counts, y_averages, y_squared_averages)]
    y_errors = list(map(lambda a: a**(1/2)/2, y_variances))
    ax.errorbar(x_bin_centers, y_averages, yerr=y_errors, xerr=x_bin_errors, c=color, label=datum_label, fmt='o')
  ax.set_xlabel(x_label)
  ax.set_ylabel(y_label)
  ax.set_xlim(x_limits[0], x_limits[1])
  ax.set_ylim(y_limits[0], y_limits[1])
  ax.legend()
  dunestyle.Simulation(ax=ax)
  return fig


### ---GENIE Comparison Analysis-------------------------------------------- ###

def get_is_initial_neutrino(datatype, particle): 
  return get_index(datatype, particle) == 0 \
         and get_pdg_code(datatype, particle) == pdg_code["tau neutrino"] \
         and get_mother_index(datatype, particle) == None
def get_is_leading_lepton(datatype, particle): 
  return get_index(datatype, particle) == 4 \
         and get_pdg_code(datatype, particle) == pdg_code["tau"] \
         and get_mother_index(datatype, particle) == 0 \
         and get_pdg_code(datatype, get_mother(datatype, particle)) == pdg_code["tau neutrino"]
def get_is_initial_atom(datatype, particle): 
  return get_index(datatype, particle) == 1 \
         and get_pdg_code(datatype, particle) == pdg_code["argon"]  \
         and get_mother_index(datatype, particle) == None

def get_energy_comparison_histogram(sample_size):
  tau_dunesw = get_attributes_dunesw([("initial_neutrino_four_momenta", get_four_momentum, get_is_initial_neutrino)],
                                     "prodgenie_nutau_dune10kt_gen.root",
                                     sample_size)
  tau_dunesw["initial_neutrino_energies"] = list(map(get_energy, tau_dunesw["initial_neutrino_four_momenta"]))
  tau_standalone = get_attributes_gtrac([("initial_neutrino_four_momenta", get_four_momentum, get_is_initial_neutrino)],
                                        "../genie-comparison/standalone/gntp.6.gtrac.root",
                                        sample_size)
  tau_standalone["initial_neutrino_energies"] = list(map(get_energy, tau_standalone["initial_neutrino_four_momenta"]))
  return get_one_parameter_histogram([tau_dunesw["initial_neutrino_energies"], tau_standalone["initial_neutrino_energies"]],
                                     ["dunesw genie", "standalone genie"], ["#D55E00", "#56B4E9"],
                                     "Initial neutrino energy (GeV)", "Number of events",
                                     (0,101), 100)

def get_energy_loss_comparison_histogram(sample_size):
  attribute_definitions = [("initial_neutrino_four_momenta", get_four_momentum, get_is_initial_neutrino),
                           ("leading_lepton_four_momenta", get_four_momentum, get_is_leading_lepton)]

  tau_dunesw = get_attributes_dunesw(attribute_definitions, "prodgenie_nutau_dune10kt_gen.root", sample_size)
  tau_dunesw["initial_neutrino_energies"] = list(map(get_energy, tau_dunesw["initial_neutrino_four_momenta"]))
  tau_dunesw["leading_lepton_energies"] = list(map(get_energy, tau_dunesw["leading_lepton_four_momenta"]))
  tau_dunesw["lepton_energy_losses"]= list(map(get_lepton_energy_loss, tau_dunesw["initial_neutrino_energies"], tau_dunesw["leading_lepton_energies"]))

  tau_standalone = get_attributes_gtrac(attribute_definitions, "../genie-comparison/standalone/gntp.6.gtrac.root", sample_size)
  tau_standalone["initial_neutrino_energies"] = list(map(get_energy, tau_standalone["initial_neutrino_four_momenta"]))
  tau_standalone["leading_lepton_energies"] = list(map(get_energy, tau_standalone["leading_lepton_four_momenta"]))
  tau_standalone["lepton_energy_losses"]= list(map(get_lepton_energy_loss, tau_standalone["initial_neutrino_energies"], tau_standalone["leading_lepton_energies"]))

  return get_one_parameter_histogram([tau_dunesw["lepton_energy_losses"], tau_standalone["lepton_energy_losses"]],
                                     ["dunesw genie", "standalone genie"], ["#D55E00", "#56B4E9"],
                                     "Lepton energy loss (GeV)", "Number of events",
                                     (0,101), 100)

def get_scattering_angle_comparison_histogram(sample_size):
  attribute_definitions = [("initial_neutrino_four_momenta", get_four_momentum, get_is_initial_neutrino),
                           ("leading_lepton_four_momenta", get_four_momentum, get_is_leading_lepton)]

  tau_dunesw = get_attributes_dunesw(attribute_definitions, "prodgenie_nutau_dune10kt_gen.root", sample_size)
  tau_dunesw["initial_neutrino_momenta"] = list(map(get_momentum, tau_dunesw["initial_neutrino_four_momenta"]))
  tau_dunesw["leading_lepton_momenta"] = list(map(get_momentum, tau_dunesw["leading_lepton_four_momenta"]))
  tau_dunesw["lepton_scattering_angles"]= list(map(get_scattering_angle, tau_dunesw["initial_neutrino_momenta"], tau_dunesw["leading_lepton_momenta"]))

  tau_standalone = get_attributes_gtrac(attribute_definitions, "../genie-comparison/standalone/gntp.6.gtrac.root", sample_size)
  tau_standalone["initial_neutrino_momenta"] = list(map(get_momentum, tau_standalone["initial_neutrino_four_momenta"]))
  tau_standalone["leading_lepton_momenta"] = list(map(get_momentum, tau_standalone["leading_lepton_four_momenta"]))
  tau_standalone["lepton_scattering_angles"]= list(map(get_scattering_angle, tau_standalone["initial_neutrino_momenta"], tau_standalone["leading_lepton_momenta"]))

  return get_one_parameter_histogram([tau_dunesw["lepton_scattering_angles"], tau_standalone["lepton_scattering_angles"]],
                                     ["dunesw genie", "standalone genie"], ["#D55E00", "#56B4E9"],
                                     "Lepton scattering angle (rad)", "Number of events",
                                     (0,3.1415/2), 100)

def get_interaction_type_bar_graph(sample_size):
  tau_dunesw = get_attributes_dunesw([("nuance_codes", get_nuance_code, None), ("scattering_codes", get_scattering_code, None)], "prodgenie_nutau_dune10kt_gen.root", sample_size)
  tau_dunesw["nuance_types"] = [get_interaction_type(nuance_code, "nuance") for nuance_code in tau_dunesw["nuance_codes"]]
  tau_dunesw["scattering_types"] = [get_interaction_type(scattering_code, "scattering") for scattering_code in tau_dunesw["scattering_codes"]]
  tau_dunesw["interaction_types"] = [get_simple_interaction_type(get_type_fallback(nuance_type, scattering_type)) for (nuance_type, scattering_type) in zip(tau_dunesw["nuance_types"], tau_dunesw["scattering_types"])]

  tau_standalone = get_attributes_gst([("nuance_codes", get_nuance_code, None), ("neut_codes", get_neut_code, None)], "../genie-comparison/standalone/gntp.6.gst.root", sample_size)
  tau_standalone["nuance_types"] = [get_interaction_type(nuance_code, "nuance") for nuance_code in tau_standalone["nuance_codes"]]
  tau_standalone["neut_types"] = [get_interaction_type(neut_code, "neut") for neut_code in tau_standalone["neut_codes"]]
  tau_standalone["interaction_types"] = [get_simple_interaction_type(get_type_fallback(nuance_type, neut_type)) for (nuance_type, neut_type) in zip(tau_standalone["nuance_types"], tau_standalone["neut_types"])]

  tau_dunesw_interaction_percent = {k: v/sample_size*100 for k, v in count_elts(tau_dunesw["interaction_types"]).items()}
  tau_standalone_interaction_percent = {k: v/sample_size*100 for k, v in count_elts(tau_standalone["interaction_types"]).items()}
  interaction_type_pairs = get_knitted_dictionaries(tau_dunesw_interaction_percent, tau_standalone_interaction_percent) 
  return get_double_bar_graph(dict(sorted(interaction_type_pairs.items(), key=lambda item: item[1], reverse=True)),
                              ["dunesw genie", "standalone genie"], ["#D55E00", "#56B4E9"], "Percent of events")


### --Tau Decay Analysis---------------------------------------------------- ###

def read_interaction_types(sample_size):
  attribute_definitions = [("nuance_codes", get_nuance_code, None),
                           ("scattering_codes", get_scattering_code, None)]
  tau_dunesw = get_attributes_dunesw(attribute_definitions, "prodgenie_nutau_dune10kt_gen.root", sample_size)
  tau_dunesw["nuance_types"] = [get_interaction_type(nuance_code, "nuance") for nuance_code in tau_dunesw["nuance_codes"]]
  tau_dunesw["scattering_types"] = [get_interaction_type(scattering_code, "scattering") for scattering_code in tau_dunesw["scattering_codes"]]
  tau_dunesw["interaction_types"] = [get_simple_interaction_type(get_type_fallback(nuance_type, scattering_type)) for (nuance_type, scattering_type) in zip(tau_dunesw["nuance_types"], tau_dunesw["scattering_types"])]
  return tau_dunesw

def read_topologies(sample_size):
  attribute_definitions = [("topologies", get_name, get_is_final_state),
                           ("decay_topologies", get_name, get_is_lepton_decay_topology),
                           ("nuclear_topologies", get_name, get_is_interaction_topology)]
  tau_dunesw = get_attributes_dunesw(attribute_definitions, "prodgenie_nutau_dune10kt_gen.root", sample_size)
  tau_dunesw["tau_decay_types"] = [get_tau_decay_type(count_elts(product_set)) for product_set in tau_dunesw["decay_topologies"]]
  return tau_dunesw

def read_charged_hadron_kinematics(sample_size):
  def get_angle_from_momenta(a, b): return get_scattering_angle(get_momentum(a), get_momentum(b))
  def get_angles_from_momenta(xs, ys): return [list(map(get_angle_from_momenta, x, [y]*len(x))) for (x,y) in zip(xs, ys)]
  attribute_definitions = [("initial_neutrino_four_momenta", get_four_momentum, get_is_initial_neutrino),
                           ("decay_charged_hadron_four_momenta", get_four_momentum, get_is_signal_charged_hadron),
                           ("nuclear_charged_hadron_four_momenta", get_four_momentum, get_is_background_charged_hadron)]
  tau_dunesw = get_attributes_dunesw(attribute_definitions, "prodgenie_nutau_dune10kt_gen.root", sample_size)
  tau_dunesw["initial_neutrino_four_momenta"] = flatten(tau_dunesw["initial_neutrino_four_momenta"])
  tau_dunesw["decay_charged_hadron_energies"] = [list(map(get_energy, row)) for row in tau_dunesw["decay_charged_hadron_four_momenta"]]
  tau_dunesw["nuclear_charged_hadron_energies"] =[list(map(get_energy, row)) for row in tau_dunesw["nuclear_charged_hadron_four_momenta"]] 
  tau_dunesw["decay_charged_hadron_momenta"] = [list(map(get_momentum, row)) for row in tau_dunesw["decay_charged_hadron_four_momenta"]]
  tau_dunesw["nuclear_charged_hadron_momenta"] =[list(map(get_momentum, row)) for row in tau_dunesw["nuclear_charged_hadron_four_momenta"]] 
  tau_dunesw["decay_charged_hadron_angles"] = get_angles_from_momenta(tau_dunesw["decay_charged_hadron_four_momenta"], tau_dunesw["initial_neutrino_four_momenta"])
  tau_dunesw["nuclear_charged_hadron_angles"] = get_angles_from_momenta(tau_dunesw["nuclear_charged_hadron_four_momenta"], tau_dunesw["initial_neutrino_four_momenta"])
  return tau_dunesw

## -- ##

def get_charged_hadron_energy_histogram(sample_size):
  tau_dunesw = read_charged_hadron_kinematics(sample_size)
  return get_one_parameter_histogram([flatten(tau_dunesw["decay_charged_hadron_energies"]), flatten(tau_dunesw["nuclear_charged_hadron_energies"])],
                                     ["tau decay", "atomic interaction"], ["#D55E00", "#56B4E9"],
                                     "Energy of charged hadrons (GeV)", "Number of events",
                                     (0,20), 100)

def get_charged_hadron_angle_histogram(sample_size):
  tau_dunesw = read_charged_hadron_kinematics(sample_size)
  return get_one_parameter_histogram([flatten(tau_dunesw["decay_charged_hadron_angles"]), flatten(tau_dunesw["nuclear_charged_hadron_angles"])],
                                     ["tau decay", "atomic interaction"], ["#D55E00", "#56B4E9"],
                                     "Angle of charged hadrons (rad)", "Number of events",
                                     (0,3.1415), 100)

def get_charged_hadron_counts(sample_size):
  charged_hadrons = ["pi+", "pi-", "K+", "K-"]
  tau_dunesw = read_topologies(sample_size)
  tau_dunesw["decay_charged_hadron_counts"] = [sum([1 for particle in topology if particle in charged_hadrons]) for topology in tau_dunesw["decay_topologies"] if topology is not None]
  tau_dunesw["nuclear_charged_hadron_counts"] = [sum([1 for particle in topology if particle in charged_hadrons]) for topology in tau_dunesw["nuclear_topologies"] if topology is not None]
  return tau_dunesw

def get_charged_hadron_count_histogram(sample_size):
  tau_dunesw = get_charged_hadron_counts(sample_size)
  return get_one_parameter_histogram([tau_dunesw["decay_charged_hadron_counts"], tau_dunesw["nuclear_charged_hadron_counts"]],
                                     ["tau decay", "atomic interaction"], ["#D55E00", "#56B4E9"],
                                     "Number of charged hadrons", "Number of events",
                                     (0,10), 10)

def get_charged_hadron_count_histogram_split(sample_size):
  tau_dunesw = get_charged_hadron_counts(sample_size)
  tau_dunesw.update(read_interaction_types(sample_size))
  decay_data = [x for (x, y) in zip(tau_dunesw["decay_charged_hadron_counts"], tau_dunesw["interaction_types"])]
  nuclear_data0 = [x for (x, y) in zip(tau_dunesw["nuclear_charged_hadron_counts"], tau_dunesw["interaction_types"]) if y == "QE"]
  nuclear_data1 = [x for (x, y) in zip(tau_dunesw["nuclear_charged_hadron_counts"], tau_dunesw["interaction_types"]) if y == "RES"]
  nuclear_data2 = [x for (x, y) in zip(tau_dunesw["nuclear_charged_hadron_counts"], tau_dunesw["interaction_types"]) if y == "DIS"]
  nuclear_data3 = [x for (x, y) in zip(tau_dunesw["nuclear_charged_hadron_counts"], tau_dunesw["interaction_types"]) if y == "MEC"]
  return get_one_parameter_histogram([decay_data, nuclear_data0, nuclear_data1, nuclear_data2, nuclear_data3],
                                     ["tau decay", "nuclear interaction QE", "nuclear interaction RES", "nuclear interaction DIS", "nuclear interaction MEC"],
                                     ["#000000", "#56B4E9", "#D55E00", "#009E73", "#E69F00"],
                                     "Prong (# of charged hadrons)", "Number of events",
                                     (0,10), 10)


### --Hadronic 1-prong 1pi0 channel----------------------------------------- ###

def get_charged_hadron_angle_1prong_1pi0_histogram(sample_size):
  tau_dunesw = read_charged_hadron_kinematics(sample_size)
  tau_dunesw.update(read_topologies(sample_size))
  decay_data = flatten([angles for (angles,decay_type) in zip(tau_dunesw["decay_charged_hadron_angles"], tau_dunesw["tau_decay_types"]) if decay_type == "h- pi0 nu(tau)"])
  nuclear_data = flatten([angles for angles in tau_dunesw["nuclear_charged_hadron_angles"]])
  return get_one_parameter_histogram([decay_data, nuclear_data],
                                     [r"$\tau\ \to\ h^- \pi^0 \nu_\tau$" "\n" "charged hadrons", "atomic interaction" "\n" "charged hadrons"], dune_colors[0:2],
                                     "Angle of charged hadrons (rad)", "Number of events",
                                     (0,3.1415), 100)

def get_charged_hadron_angle_1prong_1pi0_min_background_histogram(sample_size):
  tau_dunesw = read_charged_hadron_kinematics(sample_size)
  tau_dunesw.update(read_topologies(sample_size))
  decay_data = flatten([angles for (angles,decay_type) in zip(tau_dunesw["decay_charged_hadron_angles"], tau_dunesw["tau_decay_types"]) if decay_type == "h- pi0 nu(tau)"])
  nuclear_data = [min(angles) for angles in tau_dunesw["nuclear_charged_hadron_angles"] if angles not in [None,[]]]
  return get_one_parameter_histogram([decay_data, nuclear_data],
                                     [r"$\tau\ \to\ h^- \pi^0 \nu_\tau$" "\n" "charged hadrons", "atomic interaction" "\n" "min angle charged hadrons"], dune_colors[0:2],
                                     "Angle (rad)", "Events (PDF)",
                                     (0,3.1415), 100)

def get_charged_hadron_angle_vs_energy_1prong_1pi0_min_angle_scatter(sample_size):
  tau_dunesw = read_charged_hadron_kinematics(sample_size)
  tau_dunesw.update(read_topologies(sample_size))
  decay_xs = flatten([energies for (energies,decay_type) in zip(tau_dunesw["decay_charged_hadron_energies"], tau_dunesw["tau_decay_types"]) if decay_type == "h- pi0 nu(tau)"])
  decay_ys = flatten([angles for (angles,decay_type) in zip(tau_dunesw["decay_charged_hadron_angles"], tau_dunesw["tau_decay_types"]) if decay_type == "h- pi0 nu(tau)"])
  #nuclear_xs = flatten([energies for energies in tau_dunesw["nuclear_charged_hadron_energies"]])
  #nuclear_ys = flatten([angles for angles in tau_dunesw["nuclear_charged_hadron_angles"]])
  nuclear_xs = flatten_1d([[energy for (energy, angle) in zip(energies, angles) if angle == min(angles)] for (energies, angles) in zip(tau_dunesw["nuclear_charged_hadron_energies"], tau_dunesw["nuclear_charged_hadron_angles"]) if angles not in [None,[]]])
  nuclear_ys = flatten_1d([[angle for (energy, angle) in zip(energies, angles) if angle == min(angles)] for (energies, angles) in zip(tau_dunesw["nuclear_charged_hadron_energies"], tau_dunesw["nuclear_charged_hadron_angles"]) if angles not in [None,[]]])
  return get_scatter_plot([decay_xs, nuclear_xs], [decay_ys, nuclear_ys],
                          [r"$\tau\ \to\ h^- \pi^0 \nu_\tau$" "\n" "charged hadrons", "atomic interaction" "\n" "charged hadrons"],
                          dune_colors[0:2],
                          "Energy (GeV)", "Angle (rad)",
                          (0,100), (0,3.1415))

def get_charged_hadron_angle_vs_energy_1prong_1pi0_min_angle_profile_histogram(sample_size):
  tau_dunesw = read_charged_hadron_kinematics(sample_size)
  tau_dunesw.update(read_topologies(sample_size))
  decay_xs = flatten([energies for (energies,decay_type) in zip(tau_dunesw["decay_charged_hadron_energies"], tau_dunesw["tau_decay_types"]) if decay_type == "h- pi0 nu(tau)"])
  decay_ys = flatten([angles for (angles,decay_type) in zip(tau_dunesw["decay_charged_hadron_angles"], tau_dunesw["tau_decay_types"]) if decay_type == "h- pi0 nu(tau)"])
  nuclear_xs = flatten_1d([[energy for (energy, angle) in zip(energies, angles) if angle == min(angles)] for (energies, angles) in zip(tau_dunesw["nuclear_charged_hadron_energies"], tau_dunesw["nuclear_charged_hadron_angles"]) if angles not in [None,[]]])
  nuclear_ys = flatten_1d([[angle for (energy, angle) in zip(energies, angles) if angle == min(angles)] for (energies, angles) in zip(tau_dunesw["nuclear_charged_hadron_energies"], tau_dunesw["nuclear_charged_hadron_angles"]) if angles not in [None,[]]])
  return get_profile_histogram([decay_xs, nuclear_xs], [decay_ys, nuclear_ys],
                               [r"$\tau\ \to\ h^- \pi^0 \nu_\tau$" "\n" "charged hadrons", "atomic interaction" "\n" "min angle charged hadrons"],
                               dune_colors[0:2],
                               "Energy (GeV)", "Angle (rad)",
                               (0,20), (0,3.1415/2), 40)

def get_charged_hadron_energy_vs_angle_1prong_1pi0_min_energy_profile_histogram(sample_size):
  tau_dunesw = read_charged_hadron_kinematics(sample_size)
  tau_dunesw.update(read_topologies(sample_size))
  decay_xs = flatten([energies for (energies,decay_type) in zip(tau_dunesw["decay_charged_hadron_energies"], tau_dunesw["tau_decay_types"]) if decay_type == "h- pi0 nu(tau)"])
  decay_ys = flatten([angles for (angles,decay_type) in zip(tau_dunesw["decay_charged_hadron_angles"], tau_dunesw["tau_decay_types"]) if decay_type == "h- pi0 nu(tau)"])
  nuclear_xs = flatten_1d([[angle for (energy, angle) in zip(energies, angles) if energy == min(energies)] for (energies, angles) in zip(tau_dunesw["nuclear_charged_hadron_energies"], tau_dunesw["nuclear_charged_hadron_angles"]) if angles not in [None,[]]])
  nuclear_ys = flatten_1d([[energy for (energy, angle) in zip(energies, angles) if energy == min(energies)] for (energies, angles) in zip(tau_dunesw["nuclear_charged_hadron_energies"], tau_dunesw["nuclear_charged_hadron_angles"]) if angles not in [None,[]]])
  return get_profile_histogram([decay_xs, nuclear_xs], [decay_ys, nuclear_ys],
                               [r"$\tau\ \to\ h^- \pi^0 \nu_\tau$" "\n" "charged hadrons", "atomic interaction" "\n" "min energy charged hadrons"],
                               dune_colors[0:2],
                               "Angle (rad)", "Energy (GeV)",
                               (0,3.1415), (0,5), 40)

