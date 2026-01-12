# curling
curling mixed doubles


train bayesian model:
The Bayesian regression model was evaluated using an 80:20 train–test split. Performance on the held-out test set was assessed using Root Mean Squared Error (RMSE), Mean Absolute Error (MAE), Bias, and the coefficient of determination ($R^2$). These metrics were chosen to evaluate both predictive accuracy and calibration, with particular emphasis on MAE as a measure of practical scoring error per end. As the model is used to estimate expected values within Monte Carlo Tree Search rather than to predict exact outcomes, relative accuracy and stability are more critical than maximizing explained variance.
