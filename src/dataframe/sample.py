def take_sample(df, margin_of_error_percent=0.03):
    """Takes a sample from a DataFrame.

    Parameters:
    - df (pandas.DataFrame): The DataFrame from which to take the sample.
    - margin_of_error_percent (float, optional): The desired margin of error as a percentage. Default is 0.03.

    Returns:
    - sample (pandas.DataFrame): The sampled DataFrame.
    - description (str): A markdown description of the sampling process.

    If the sample size is smaller than the size of the original DataFrame, a random sample of
    the specified size is taken. Otherwise, the original DataFrame is returned as is.

    The description provides information about the sampling process, including the sample size,
    confidence level, and margin of error.
    If the sample size is smaller than the size of the original DataFrame, the description is None.
    """

    # Let's calculate sample size for behaviour of infinite human population with:
    # 50% population proportion (measured values can be higher or lower than true values),
    # 95% confidence level,
    # and set margin of error
    sample_size = int(round(pow(1.96, 2) * 0.25 / pow(margin_of_error_percent, 2)))

    description = None
    sample = df
    df_len = len(df)

    if sample_size < df_len:
        description = f"**Disclaimer**: the following report has been produced using a sample\
                of {sample_size} random records from the original dataset of {df_len} records\
                to do estimations at a 95% confidence level \
                with a {int(margin_of_error_percent*100)}% margin of error."

        sample = df.sample(sample_size).sort_index()

    return sample, description
