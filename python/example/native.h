#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct ShippaiError ShippaiError;

char *authenticate(const char *user, const char *pass, ShippaiError **c_err);

void shippai_free_failure(ShippaiError *t);

void shippai_free_str(char *t);

const char *shippai_get_cause_display(ShippaiError *t);

const char *shippai_get_cause_name(ShippaiError *t);

const char *shippai_get_cause_names();
