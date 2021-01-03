import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

# fit a normal distribution, number_count is how many we want to average
def get_normal_dist_params(vals, probs, number_count=1, ):
  # mean stays the same
  normal_mean = np.sum(np.array(vals) * np.array(probs))
  # average n values, variance is divided by n
  normal_variance = np.sum(np.power(vals - normal_mean, 2) * probs) / number_count
  return normal_mean, np.sqrt(normal_variance)

# plot a normal fit for the data, given values, probs, and how many we average over
def plot_normal_fit(vals, probs, avg_count, label='Normal Distribution Fit'):
  normal_mean, normal_std = get_normal_dist_params(vals, probs, avg_count)
  plt_x_vals = np.linspace(normal_mean - 3 * normal_std, normal_mean + 3 * normal_std, 100)
  dist_vals = np.array([stats.norm.pdf(x, loc=normal_mean, scale=normal_std) for x in plt_x_vals]) # calculate the value of distribution in different configs
  plt.plot(plt_x_vals, dist_vals, label=label)
