# MIR-level optimizations

`copy_prop.rs` Copy propagation, optimization.

`cross_crate_inline.rs` Cross crate inline, optimization?

`dataflow_const_prop.rs` Constant propagation based on dataflow analysis, optimization.

`dead_store_elimination.rs` DSE, optimization.

`dest_prop.rs` Destination propagation. Propagate assignments backward in the CFG to eliminate redundant assignments. "LLVM is not good enough at this". Good description of optimization in comments.

`early_otherwise_branch.rs` Match on two enums optimizaton, example in comments.

`gvn.rs` Global value numbering on MIR.

`impossible_predicates.rs` Check if `where` clause contains provably unsatisfiable predicates.

`inline.rs` Inlining pass for MIR functions.

`instsimplify.rs` MIR peephole optimizations.

`jump_threading.rs` Jump threading optimization.

`large_enums.rs` Optimize memcpy of enums with large differences between variant sizes.

`match_branches.rs` Merge BBs that differ only in const bool assignments.

`multiple_return_terminators.rs` Replace jumps to BBs with only return with just a return.

`nrvo.rs` NRVO (transform MIR so that LLVM performs the optimization).

`ref_prop.rs` Propagate references using SSA analysis.

`remove_noop_landing_pads.rs` Remove noop landing pads ("LLVM generated terrible code for them")

`remove_uninit_drops.rs` Remove drops for items that are known to be unitialized.

`remove_uneeded_drops.rs` Remove drop for types that do not need dropping.

`remove_zsts.rs` Remove operations on ZST places and convert ZST operands to constants.

`simplify_branches.rs` Replace branch with goto if condition is known.

`simplify_comparison_integral.rs` Convert `if` on integral values into switches.

`single_use_consts.rs` Remove constants with no uses or single use (GVN does this, but only on higher optimization levels).

`sroa.rs` Scalar Replacement Of Aggregates.

`unreachable_enum_branching.rs` Remove branches on uninhabited or unreachable enum variants.

`unreachable_prop.rs` Propagate unreachable block terminators.

# Misc/unsorted

`abort_unwinding_calls.rs` Handle unwinds in FFI function when panic=abort, not an optimization.

`add_call_guards.rs` Break CFG critical edges, not an optimization.

`add_moves_for_packed_drops.rs` Handle make drops in packed structs from aligned addresses, not an optimization.

`add_subtyping_projection.rs` Make subtyping explicit in MIR, not an optimization.

`add_retag.rs` MIR building pass, not an optimization.

`check_alignment.rs` Insert alignment checks, not an optimization.

`check_*.rs` Insert some kind of check (not all files have been inspected).

`cleanup_post_borrowck.rs` Cleanup MIR after analysis and borrowck.

`coroutine.rs` Transform coroutines into state machines, not an optimization.

`cost_checker.rs` Inline cost calculation, not an optimization.

`ctfe_limit.rs` Insert markers for loops in CFG, not an optimization.

`deduce_param_attrs.rs` Deduce param attributes from function body.

`deref_separator.rs` ?

`dump_mir.rs` Dump MIR, not an optimization.

`elaborate_box_derefs.rs` Transform deref on Box to deref on pointer inside Box (deref on Box is sugar).

`elaborate_drop.rs`, `elaborate_drops.rs` Something about Drops?

`errors.rs` Different lints and errors.

`ffi_unwind_calls.rs` Check if ffi can leak unwind into Rust code.

`function_item_references.rs` Some function reference lints?

`known_panics_list.rs` Lint for known panics (e.g. overflow, division by zero)

`lint.rs` More lints.

`lint_tail_expr_drop_order.rs` More lints.

`lower_intrinsics.rs` Lower intrinsic calls.

`lower_slice_len.rs` Lower calls to slice len to `PtrMetadata`.

`mentioned_items.rs` ?

`pass_manager.rs` Pass manager.

`patch.rs` Struct for modifying MIR.

`post_analysis_normalize.rs` Normalize MIR.

`post_drop_elaboration.rs` Lint?

`prettify.rs` 'Prettify' MIR, no value to compiler.

`promote_consts.rs` Promote borrows of constant rvalues?

`remove_place_mention.rs` Remove `PlaceMention` op, which has no effect on codegen.

`remove_storage_markers.rs` Remove storage markers if they won't be emitted during codegen.

`required_consts.rs` ?

`sanity_check.rs` Dataflow sanity check?

`shim.rs` ?

`simplify.rs` SimplifyCFG + SimplifyLocals.

`ssa_locals.rs` Analyze SSA locals (one assignment which dominates all uses).

`strip_debuginfo.rs` Remove some debuginfo in MIR.

`validate.rs` Validate MIR.
