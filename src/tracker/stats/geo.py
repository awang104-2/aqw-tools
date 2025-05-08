import numpy as np
import scipy.stats as stats


def p_estimate(x: np.typing.ArrayLike, method: str = 'mle'):
    """
    Probability parameter point estimator for a sample of geometric random variables.
    :param x: Sample data as an ArrayLike of ints where each int is the number of trials including success
    :param method: Type of point estimator
    :return: Probability of a single Bernoulli trial and sample variance as a tuple
    """
    p, var = (None, None)
    match method:
        case 'mle':
            p = 1 / np.mean(x)
            var = (1 - p) * p ** 2 / len(x)
        case 'mom':
            p = 1 / np.mean(x)
            var = (1 - p) * p ** 2 / len(x)
    if p and var:
        return p, var
    else:
        raise ValueError('Invalid point estimator type.')


def margin_of_error(probability, variance, confidence=0.95):
    """
    Uses CLT to calculate the margin of error for a point estimate of a sample of geometric random variables.
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


def cdf(x, p):
    """
    Calculates the probability of x or less successes using the cumulative distribution function provided by scipy.
    :param x: Number of trials
    :param p: Probability of a single Bernoulli trial
    :return: Probability of x number of trials or less
    """
    return stats.geom.cdf(x, p)


def pmf(x, p):
    """
    Calculates the probability of x successes using the probability mass function provided by scipy.
    :param x: Number of trials
    :param p: Probability of a single Bernoulli trial
    :return: Probability of x number of trials
    """
    return stats.geom.pmf(x, p)


def inv_cdf(P, p):
    """
    Evaluates the inverse CDF of a geometric random variable.
    :param P: Percentile of geometric distribution
    :param p: Probability of a single Bernoulli trial
    :return: Number of trials
    """
    return stats.geom.ppf(P, p=p)



