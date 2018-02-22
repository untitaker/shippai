#[macro_use] extern crate shippai;
#[macro_use] extern crate failure;

use std::os::raw::c_char;
use std::ffi::{CStr,CString};
use std::ptr;

#[derive(Debug, Fail)]
pub enum MyError {
    #[fail(display = "Invalid username")]
    UserWrong,
    #[fail(display = "Invalid password")]
    PassWrong 
}

/// The functionality we want to export
fn authenticate_impl(user: Option<&str>, pass: Option<&str>) -> Result<String, failure::Error> {
    if user != Some("admin") { return Err(MyError::UserWrong.into()); }
    if pass != Some("password") { return Err(MyError::PassWrong.into()); }
    Ok(String::from("Hello world!"))
}

pub mod exports {
    use super::*;
    // The macro generates a few extern functions prefixed with `shippai_` and constants prefixed
    // with `SHIPPAI_`. It also generates a public type `ShippaiError` which is a wrapper around
    // `failure::Error` and can be converted from and into it.
    shippai_export!{
        // MyError is the type we want to export, and MY_ERROR is the name as which it should be
        // visible through FFI. For now both are required to avoid confusion between `foo::Error`
        // and `bar::Error`.
        //
        // The Python side will convert `MY_ERROR` back to `MyError` for idiomaticity.
        MyError as MY_ERROR
    }
}

/// The exported variant of `authenticate_impl`. The caller passes in a pointer to a nullpointer
/// for `c_err`. If the inner pointer is still NULL after the call, the call succeeded.
#[no_mangle]
pub unsafe extern "C" fn authenticate(user: *const c_char, pass: *const c_char,
                                      c_err: *mut *mut exports::ShippaiError) -> *mut c_char {
    let res = authenticate_impl(
        CStr::from_ptr(user).to_str().ok(),
        CStr::from_ptr(pass).to_str().ok()
    );

    export_result(res, c_err)
        .map(|x| CString::new(x).unwrap().into_raw())
        .unwrap_or(ptr::null_mut())
}

/// A helper function for converting "normal" results into the corresponding extern types.
///
/// This could be part of shippai itself sometime. Feedback welcome.
unsafe fn export_result<V>(res: Result<V, failure::Error>, c_err: *mut *mut exports::ShippaiError) -> Option<V> {
    match res {
        Ok(v) => Some(v),
        Err(e) => {
            *c_err = Box::into_raw(Box::new(e.into()));
            None
        }
    }
}
