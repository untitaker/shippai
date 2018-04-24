#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct ShippaiError ShippaiError;

extern const uint8_t SHIPPAI_VARIANT_MyError_PassWrong;

extern const uint8_t SHIPPAI_VARIANT_MyError_UserWrong;

/*
 * The exported variant of `authenticate_impl`. The caller passes in a pointer to a nullpointer
 * for `c_err`. If the inner pointer is still NULL after the call, the call succeeded.
 */
char *authenticate(const char *user, const char *pass, ShippaiError **c_err);

void shippai_free_failure(ShippaiError *t);

void shippai_free_str(char *t);

const char *shippai_get_debug(ShippaiError *t);

const char *shippai_get_display(ShippaiError *t);

uint8_t shippai_get_variant_MyError(ShippaiError *t);

bool shippai_is_error_MyError(ShippaiError *t);
