import numpy as np
import scipy.stats as stats


class MaxIterationsExceeded(Exception):
    pass


def p_estimate(x: int, n: int, method: str = 'mle'):
    """
    Probability parameter point estimator for a sample of Bernoulli random variables.
    :param x: Sample data, equal to the number of successes
    :param n: Sample size
    :param method: Type of point estimator
    :return: Probability of a single Bernoulli trial and sample variance as a tuple
    """
    p, var = (None, None)
    match method:
        case 'mle':
            p = x / n
            var = p * (1 - p) / n
        case 'mom':
            p = x / n
            var = p * (1 - p) / n
    if p and var:
        return p, var
    else:
        raise ValueError('Invalid point estimator type.')


def margin_of_error(probability, variance, confidence=0.95):
    """
    Uses CLT to calculate the margin of error for a point estimate of a sample of Bernoulli random variables.
    :param probability: Probability parameter estimate, p
    :param variance: Variance of probability parameter, Var(p)
    :param confidence: Percent confidence, 95% by default
    :return: Margin of error
    """
    if confidence >= 1 or confidence <= 0:
        raise ValueError('Confidence needs to be between 0 and 1.')
    mean, std = (probability, np.sqrt(variance))
    dist = stats.norm(mean, std)
    return dist.ppf(confidence / 2)


def cdf(x, p, n):
    """
    Calculates the probability of x or less successes using the cumulative distribution function provided by scipy.
    :param x: Number of successes
    :param p: Probability of a single Bernoulli trial
    :param n: Number of Bernoulli trials
    :return: Probability of x number of successes or less
    """
    return stats.binom.cdf(x, n, p)


def pmf(x, p, n):
    """
    Calculates the probability of x successes using the probability mass function provided by scipy.
    :param x: Number of successes
    :param p: Probability of a single Bernoulli trial
    :param n: Number of Bernoulli trials
    :return: Probability of x number of successes
    """
    return stats.binom.pmf(x, n, p)


def inv_cdf(P, n, p):
    """
    Evaluates the inverse CDF of a binomial random variable.
    :param P: Percentile of the binomial distribution
    :param n: Number of trials
    :param p: Probability of a single Bernoulli trial
    :return: Number of successes
    """
    return stats.geom.ppf(P, n=n, p=p)


def _min_n(P, x, p):
    n = 0
    iter = 0
    while True:
        if 1 - cdf(x - 1, p, n) - P >= 0:
            print("Iterations:", iter)
            return n
        else:
            n += 1
            iter += 1


def min_n(P, x, p):
    prev_diff = -100
    f = lambda n: 1 - P - cdf(x - 1, p, n)
    n0, n1 = np.array([x / p, 2 * x / p]).astype(int)
    max_iterations = int(10 * x / p ** 2)
    for i in range(max_iterations):
        diff = f(n1) * (n1 - n0) / (f(n1) - f(n0))
        if diff > 0 > prev_diff and int(prev_diff) == 0 and int(diff) == 0:
            print('Iterations:', i + 1)
            return n1
        elif int(diff) == 0:
            n0 = n1
            n1 -= np.sign(diff).astype(int)
            if n1 < 0:
                n1 = 0
            prev_diff = diff
        else:
            n0 = n1
            n1 -= int(diff)
            prev_diff = diff
            if n1 < 0:
                n1 = 0
    raise MaxIterationsExceeded(f'Maximum iterations {max_iterations} exceeded.')



