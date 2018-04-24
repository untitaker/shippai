extern crate proc_macro;
extern crate syn;
#[macro_use]
extern crate quote;
extern crate synstructure;

use proc_macro::TokenStream;

#[proc_macro_derive(Shippai)]
pub fn shippai(input: TokenStream) -> TokenStream {
    let ast = syn::parse(input).unwrap();
    let gen = impl_shippai(&ast);
    gen.into()
}

fn impl_shippai(ast: &syn::DeriveInput) -> quote::Tokens {
    let error_name = &ast.ident;
    let fn_name = syn::Ident::from(format!("shippai_is_error_{}", error_name));

    let variant_helpers = impl_enums(error_name, ast);

    quote! {
        #[no_mangle]
        pub unsafe extern "C" fn #fn_name(t: *mut ShippaiError) -> bool {
            (*t).error
                .downcast_ref::<#error_name>()
                .is_some()
        }

        #( #variant_helpers )*
    }
}

fn impl_enums(error_name: &syn::Ident, ast: &syn::DeriveInput) -> Option<quote::Tokens> {
    match ast.data {
        syn::Data::Enum(_) => (),
        _ => return None
    }

    let mut exported_discriminants = vec![];

    let s = synstructure::Structure::new(ast);
    let match_arms = s.each_variant(|v| {
        let name = &v.ast().ident;
        exported_discriminants.push(
            syn::Ident::from(format!("SHIPPAI_VARIANT_{}_{}", error_name, name))
        );
        let index = syn::Index::from(exported_discriminants.len());
        quote!(return #index)
    });

    let indices = (1 .. (exported_discriminants.len() + 1))
        .map(syn::Index::from);
    let fn_name = syn::Ident::from(format!("shippai_get_variant_{}", error_name));
    Some(quote! {
        #(
            #[no_mangle]
            pub static #exported_discriminants: u8 = #indices;
        )*

        #[no_mangle]
        pub unsafe extern "C" fn #fn_name(t: *mut ShippaiError) -> u8 {
            if let Some(f) = (*t).error.downcast_ref::<#error_name>() {
                match *f {
                    #match_arms
                }
            }

            0
        }
    })
}
